---
title: "Vulkan Graphics Examples - Animation"
date: 2023-08-11T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-animation-16.png
  thumbnail: /images/vge-animation-16.png
---

이전 예제에서 glTF모델 load와 관련 구조를 작성할 때, animation과 skinning관련된 부분들은 아직 쓰이지 않아 제외하고 구현했다.  
이번 예제를 통해 해당 빈 부분들의 기능을 추가했다.  

> [https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/3](https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/3)


- [개념](#개념)
  - [skin](#skin)
  - [skinning matrix](#skinning-matrix)
  - [inverse bind matrix](#inverse-bind-matrix)
  - [animation](#animation)
    - [animation channels](#animation-channels)
    - [animation samplers](#animation-samplers)
  - [data transfer structure](#data-transfer-structure)
- [Progress](#progress)
  - [모델](#모델)
  - [Progress-0](#progress-0)
    - [fix](#fix)
  - [Progress-1](#progress-1)
    - [animation](#animation-1)
    - [instance map](#instance-map)
    - [skeleton rendering](#skeleton-rendering)
  - [Progress-2](#progress-2)
    - [bone length and orientation](#bone-length-and-orientation)
    - [bind pose or empty animation](#bind-pose-or-empty-animation)
    - [fix](#fix-1)


---

<style>
o { background-color: Orange }
g { background-color: Green }
r { background-color: Red }
</style>


# 개념
> [gltf20-reference-guide.pdf (khronos.org)](https://www.khronos.org/files/gltf20-reference-guide.pdf)

기본적인 개념은 이전과 같은 자료를 참고했다. 

## skin
mesh에 있는 여러 vertices들이 skeleton의 각 bone 위치에 영향을 받도록 해주는 기법이다.
- node는 mesh를 참조할 수 있다. (mesh가 없는 node도 있다.)
  - node는 skin도 참조할 수 있다.
- skin은 joint들로 이뤄져 있다.
  - 그리고 각 joint에 해당하는 inverse bind matrix 정보도 가지고 있는데, 이는 아래에서 설명하겠다.
  - joint는 node의 일종이다.
    - 따라서 node의 hierarchy 구조를 활용할 수 있다.
- skeleton은 따로 명시적인 구조로 저장되지 않고, joint들의 계층구조가 이를 표현한다.
- skinned mesh는 그 primitives를 통해, joint와 weight attribute를 가진다.
  - joint는 그 vertex에 영향을 줄 joint의 index다. 보통 4개로, vec4타입을 사용한다.
  - weight는 각 joint가 그 vertex에 얼마나 영향을 줄지를 나타낸다.

## skinning matrix
skeleton의 자세에 따라서 (joint들의 변환으로 결정됨) mesh의 vertices들이 어떻게 변환될지 계산한 결과이다. 이 계산에 joint matrices와 weight들이 쓰인다.  
이 skin matrix를 반영한 최종 위치는 결국 shader에서 계산되는데, 
다음과 같은 예시를 들 수 있다.  
> gl_Position = P*V*M * (nodeMat)* skinMat * inPos;  


각자의 변환을 뜯어보면,
- M: model space -> world space
  - load된 모델자체를 이동/회전/스케일링 하는 역할로 쓰인다.
- nodeMat: node(mesh) local space -> model space
  - 모델 내부의 scene graph 계층 구조를 표현하므로 별도로 필요하다.
  - 이 nodeMat이 사용되려면, mesh가 있는 node의 matrix가 있어야 하는데, 이런 자료를 많이 보진 못했다. 3D 모델링 과정 상, mesh의 좌표계를 model의 좌표계와 동일하게 보는 경우가 많은 것 같은데, [glTF-Sample-Models repo](https://github.com/KhronosGroup/glTF-Sample-Models/tree/master/2.0)를 보면, 일부 CAD 변환 데이터들에만 해당된다.
- skinMat: mesh space -> mesh space
  - $$ \sum_{i=1}^{4}{v.weight[i] * jointMatrice[v.joint[i]]} $$  
  - 한 mesh(혹은 skin)에서 사용하는 joint들의 최대 수는 64개로 정했다. (따로 제한이 있는 것 같진 않고, buffer 크기를 고려해서 정했다.)
- jointMat은 inverse global transform * global joint transform * inverse bind mat 으로 계산된다.
  - invese global transform: model space -> mesh space
    - 이 global transform은 skin을 가지고 있는 node의 matrix다.
    - 이 node를 `drawNode()` 할 때 mesh가 실제로 그려지는데, mesh의 primitives의 joint가 계산에 사용된다. 그리고 이 node의 하위에 skin이 있는게 아니라, 별도의 skin을 참조하는 것이기에 이 global transform은 shader에서 node mat을 곱하는 것을 상쇄시키도록 작용한다. 따라서 shader 구현에 따라 어떻게 계산할지가 결정된다.
    - 지금은 이게 왜 필요한지 명확히 설명되지 않았을 수 있는데, 아래에서 inverse bind matrix를 다르면서 더 자세히 설명하겠다.
  - global joint transform: joint local space -> model space
    - 자세에 따라 바뀌는 부분의 실질적 내용이다.
    - animation을 구성할때도 시간에따라 이 부분이 변경된다.
    - 이름에 global이 있듯이, 모든 hierarchy의 계산이 포함된 결과가 들어간다.
  - inverse bind matrix: mesh space -> joint local space
    - 기본 바인드 자세에서, 각 joint의 위치가 mesh 기준 어디인지 나타내는 것이 bind matrix이다. 이 matrix의 inverse를 처음에 곱해줌으로써, mesh를 joint의 local space로 보낸다.

## inverse bind matrix
guide의 설명으로는 inverse bind matrix관련 이해가 충분하지 않아 다음 자료들을 추가로 참고했다.  


> [glTF-Tutorials/gltfTutorial/gltfTutorial_020_Skins.md at master · KhronosGroup/glTF-Tutorials (github.com)](https://github.com/KhronosGroup/glTF-Tutorials/blob/master/gltfTutorial/gltfTutorial_020_Skins.md)

이 tutorial 자료에서, guide의 예시와 같은 자료가 쓰여서 이해에 도움이 된다.

> [https://lisyarus.github.io/blog/graphics/2023/07/03/gltf-animation.html](https://lisyarus.github.io/blog/graphics/2023/07/03/gltf-animation.html)

더 일반적인 animation에 관련된 설명을 하는데, 가장 이해에 도움이 많이된 자료다.
- skeleton based vs. [morph-target](https://en.wikipedia.org/wiki/Morph_target_animation)
  - 장점
    - 저장공간이 덜 든다.
    - frame마다 필요한 data straming이 적다.
      - mesh가 아니라, bone 정보만 전달하면 되니까. *(GPU 쪽에 animation 관련 데이터 전체를 저장해놓는 방법도 있긴 함)
    - artist 친화적
    - animation과 model을 분리
    - procedural animation으로 통합하기 쉽다.
      - pre-defined가 아닌 다양한 상황에서의 animation
        - 발이 땅을 통과하지 않는 것 등의 제한사항 구현
  - 단점
    - 정해진 format을 적절하게 parse, decode 해야함
    - 각 animated model의 bone의 변환을 계산해야함. (계산비용 및 구현 복잡도 -> compute shader 사용 가능)
    - bone data를 어떻게든 GPU로 보내야함
      - per vertex 정보가 아니고, uniform에 맞지 않을 수 있음.
    - bone transform을 vertex shader에서 적용해야해서 대략 4배 느려짐 (mat mul을 4번 더하니까, 그래도 fragment shader가 보통 더 느림)
      - 이 계산을 compute shader에서 할 수도 있음. 실제로 다음 예제에서 그렇게 할 예정.
      - 성능상 차이가 있을지는 모르겠음. 확인 필요.
- bone transform(joint global transform)
  - 기본적으로 joint node에 저장된 matrix를 적용하고 나서, parent의것을 적용하는 순서이다. 
  - joint local transform 이 필요한 이유는 상식적으로, 팔을 돌리는 동작을 표현할때, origin이 어깨에 있는 것이 편한 것과 같은 이유.
  - 그래서 각 bone의 local transfrom 기준은 local coorinates다. 근데 적용할 대상인 vertices들은 model(혹은 mesh)의 좌표계에 있다. (여기서 설명은 모든 mesh coordinate과 model coordinate을 동일하게 보는 것 같다.)
    - 이 차이를 없애는 map: model space -> bone local space 변환이 inverse bind matrix이다.
  - bone local을 옮기는 것이 다일까? 아니다. parent bone도 고려해야한다.
    - bone local transform을 적용 후, bind pose mat을 곱해서 local animation이 적용된 vertices들을 다시 모델의 기존 위치쪽으로 옮긴다.
    - 그 후 parent의 inv bind mat을 곱해서 parent bone의 local로 가져오는 방식을 반복한다.
    - 이 연속된 두 변환을 하나로 곱해서 다음처럼 표기하자.  
      > $$ \displaylines{converToParentCS(node) = \\ invBindMat(parent) * BindMat(node)} $$
      - 사실 glTF에서는 이 변환을 명시적으로 가지고 있지 않다.
        - artist들이나 3d model software에서 어떨때는 vertices들이 모델의 기본 state가 아니라, bind pose라고 하는 변환된 state의 bone에 붙어있게 하는것이 편할때가 있다. 그래서 vertices들을 각 bone이 bind pose에서 expects하는 좌표계로 옮기는 또다른 변환이 필요할지도 모르는데, 사실 필요없다고 한다.
        - blender에서는 world-space vertex positions가 bind pose 그 자체다. 그래서 blender에서 exported 된 animated model은 animation 없이 사용하기는 불가능하지만 효율적으로 rendering 가능한다.
          - 이 말이 잘 이해가 안가긴하는데, bind pose라는 별도의 개념없이 rest pose가 그대로 사용된다는 말 같다. (bind pose와 rest pose가 다른 sw에서는 구분되는 개념인지도 잘 모르겠지만) 캐릭터 모델의 경우 T 자세의 bind pose 자체가 기본 vertex positions여서, animation 없이는 이 T 자세의 캐릭터 밖에 못쓴다는 말로 이해했다.
- 이게 기본적인 구조인데, format에 따라 조금씩 다르다고 한다. 
  - glTF에서 node로 이뤄진 구조에서 rigging/animation 관련 내용들을 정리하면 다음과 같다.
  - armature(skeleton과 같은 뜻으로 쓰이는 것 같다.) node가 따로 있는 것이 아니고, node의 일종이다. 
  - model bind pose가 이미 모델에 적용되어 있거나, inverse bind matrix에 premultiplied 되어 있기 때문에 bind pose라는 개념을 잊어도 된다.
  - per-bone inverse bind matrices는 accessor를 통해 접근하며 buffer에 따로 저장이 되어 있다.
  - animation은 external하게 지정가능하거나, keyframe spline으로 저장되어 있다
  - 중요한 것은, 이 animation들이 localCS to parentCS 변환과 combined 되어있다는 것.
    - `converToParent()`에 해당하는 변환이 이미 위의 animation 결과에 반영이 되어있다는 뜻이다.
  - 따라서 `invBindMat(parent)` 도 필요가 없다.
- 정리해보면, grand-parert -> g-p
  > global(bone) =  
  … * <o>invBindMat(g-g-p) *  bindMat(g-p) * localTransform(g-p)</o> * <br> <g>invBindMat(g-p) * bindMat(parent) * localTransform(parent)</g> * <br> <r>invBindMat(parent) * bindMat(current) * localTransform(current)</r> * <br> invBindMat(current) =  
  … * <o>converToParent(g-p) * localTransform(g-p)</o> *  <br> <g>converToParent(p) * localTransform(parent)</g> * <br> <r>converToParent(current) * localTransform(current)</r> * <br> invBindMat(current) =   
  … * <o>animation(g-p)</o> *  <br> <g>animation(parent)</g> * <br> <r>animation(current)</r> * <br> invBindMat(current)
  - 각 색칠된 부분들이 같은 값에 대응된다고 보면 된다.
  - 이 global(bone)에 적용될 vertices는 bind pose 상태인 mesh의 vertice다.
  - 최종적으로 skin이 함께 가지고 있는 정보는, 각 bone에 해당하는 inverse bind matrices이다.

## animation

### animation channels
- target을 지정한다. target은 node와 path로 구성된다.
- path를 먼저 설명하자면, path는 translation, rotaion, scale 중 하나의 타입을 지정한다.
- node는 아래의 sampler를 통해 계산된 결과가 local transform으로 저장될 노드다.
- channel은 어떤 sampler를 사용할지도 참조한다.

### animation samplers
- sampler는 keyframe의 in/out data와 interpolation 타입으로 구성된다.
- input은 keyframes, output은 path에 해당하는 transform이다.
- 원하는 time이 어느 keyframe 구간에 속하는지 찾은 후, 그 구간에 위치한 비율에 따라 output을 interpolation한 결과 transform이 channel에 명시된 node의 local transform에 저장된다.
  - 보통 binary search를 통해 그 구간을 찾는다.
  - interpolation 방식은 linear, step, cubic spline등이 될 수 있다.
  - node가 joint에 해당하는 node이면 skinning과 결합된 animation을 만들어낸다.


## data transfer structure

- 각 model instance 의 변환
  - model instance가 움직이거나, 다른 색을 가지거나 하는 것등을 표현하기 위해 dynamic UBO를 쓰기로 결정했다.
  - 이 값은 model에 포함될 수 없다. (같은 모델이더라고, 여러개 생성해서 다른 위치에 보여주고 싶은 경우)
  - `maxUniformBufferRange`가 65536 byte일때, 4x4 matrix 하나가 64 bytes 이므로, 대략 2^10개의 model instance를 표현할 수 있으므로 충분하다고 봤다.
  - 이 dynamic UBO는 매 frame마다 update가 이뤄지므로, `MAX_FRAMES_IN_FLGHT` 수 만큼 중복해서 생성해줬다.
- skin 당 joint(bone) 의 수를 제한을 64로 뒀다.
  - 어차피 한 vertex 계산에 필요한 joint matrice는 4개이긴 하지만, 그 4개는 joint index를 통해 접근한 값이다.
  - 결국 draw전에 64개의 joint matrices 전부를 bind 해야하긴 하다.
  - node matrix와 이 joint matrices는 mesh에서 소유하는 uniform buffer로 전달한다.
  - 이때 각 joint node의 global transform을 구하는 과정에서, 매 frame마다 이 UBO의 update가 이뤄진다. 따라서 이 ubo는 `MAX_FRAMES_IN_FLGHT` 수 만큼 중복해서 생성해줬다.
  - 이 data는 크기가 크기도 하고, model마다 skin이 여러개 있을 수 있기때문에, dynamic UBO로 생성하기에는 offset mapping 도 적절치 않아 이런 구조를 사용하게 됐다.
  - 이후에 vertex shader가 아닌 compute shader에서 미리 animation을 계산할 경우에도, 모든 skin에 대해, 각 skin 하나에 해당하는 UBO의 내용을 묶어서 하나의 SSBO로 전달하고, vertex의 attribute에 skin index를 추가해주는 구조로 사용이 가능하다.

이에 해당 descriptor set 부분까지 작성을 완료하면, 다음처럼 animation이 없는 model instance를 그리는 것이 가능해진다.  

![image](/images/vge-animation-0.png)  

# Progress
## 모델
[glTF-Sample-Models/2.0/Fox at master · KhronosGroup/glTF-Sample-Models (github.com)](https://github.com/KhronosGroup/glTF-Sample-Models/tree/master/2.0/Fox)


## Progress-0

ubo
pretransform

### fix
- index
- normal


## Progress-1
### animation
### instance map
### skeleton rendering


## Progress-2

### bone length and orientation
### bind pose or empty animation
### fix
joint attributes

![image](/images/vge-animation-1.png)  
![image](/images/vge-animation-2.png)  
![image](/images/vge-animation-3.png)  
![image](/images/vge-animation-4.png)  
![image](/images/vge-animation-5.png)  
![image](/images/vge-animation-6.png)  
![image](/images/vge-animation-7.png)  
![image](/images/vge-animation-8.png)  
![image](/images/vge-animation-9.png)  
![image](/images/vge-animation-10.png)  
![image](/images/vge-animation-11.png)  
![image](/images/vge-animation-12.png)  
![image](/images/vge-animation-13.png)  
![image](/images/vge-animation-14.png)  
![image](/images/vge-animation-15.png)  
![image](/images/vge-animation-16.png)  

![image](/images/vge-animation-3.gif)  