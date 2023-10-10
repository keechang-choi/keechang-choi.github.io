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
  - [data transfer structure](#data-transfer-structure)
- [Progress](#progress)
  - [모델](#모델)
  - [Progress-0](#progress-0)
  - [Progress-1](#progress-1)
  - [Progress-2](#progress-2)


---


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
  - 이 연속된 두 변환을 다음처럼 표기하자.  
    > $$ \displaylines{converToParentCS(node) = \\ invBindeMat(parent) * invBindMat(node)^{-1}} $$
  - 

    


## data transfer structure

# Progress
## 모델
[glTF-Sample-Models/2.0/Fox at master · KhronosGroup/glTF-Sample-Models (github.com)](https://github.com/KhronosGroup/glTF-Sample-Models/tree/master/2.0/Fox)


## Progress-0
## Progress-1
## Progress-2


![image](/images/vge-animation-0.png)  
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