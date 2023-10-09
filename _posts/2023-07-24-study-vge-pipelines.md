---
title: "Vulkan Graphics Examples - Pipelines"
date: 2023-07-24T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-pipelines-1.png
  thumbnail: /images/vge-pipelines-1.png
---

이번 예제는 pipelines 예제이다. 하나의 모델을 파일로부터 로드한 후, lighting rendering, toon rendering, wireframe rendering의 세가지를 위한 각각의 pipeline을 생성해서 화면을 분할하여 보여주는 예제이다.  
사실 pipeline 생성하는 작업에 대한 내용은 많지 않고, model loading을 위한 작업이 대부분을 차지했다.

> [https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/2](https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/2)


- [glTF](#gltf)
  - [model](#model)
  - [scene](#scene)
  - [node](#node)
  - [mesh](#mesh)
  - [primitive](#primitive)
  - [material](#material)
  - [texture](#texture)
- [Loading assets](#loading-assets)
  - [flags](#flags)
  - [texture loading](#texture-loading)
  - [materials loading](#materials-loading)
  - [nodes loading](#nodes-loading)
- [draw](#draw)
  - [pipelines](#pipelines)
- [TODO](#todo)

---

# glTF
모델 loading과 관련된 내용을 먼저 작업했다. pipeline 구성을 위해선 어떤 종류의 data를 사용할지 (descriptorSetLayout)에 대한 정보가 필요했기 때문이다.   

사용한 3d model format은 glTF 라는 format인데, KhronosGroup에서 개발한 loading괴 크기 효율에 중점을 맞춘 형식이다. 기본적인 개념은 다음 정보를 참고했다.  

[https://www.khronos.org/files/gltf20-reference-guide.pdf](https://www.khronos.org/files/gltf20-reference-guide.pdf)

해당 내용들은 [vgeu_gltf.cpp](https://github.com/keechang-choi/Vulkan-Graphics-Example/blob/main/src/base/vgeu_gltf.cpp)에 구현했다. 원본의 pipelines 예제에서는 glTF 기능들을 분리하지 않고 필요한 내용들울 포함하는데, glTF 예제에는 조금 더 확장된 기능을 분리된 코드로 정리해 나가면서 다룬다. 두 예제를 합친 내용을 여기서 한번에 구현했다고 봐도 된다.  

## model
- 외부에서 사용할 가장 큰 클래스다.
  - load와 draw method를 외부에서 호출하는 구조다.
- node들을 전부 소유
- texture도 전부 소유
- material도 전부 소유
- animation등 필요한 모든 resource를 소유.
- 하위 구조들에서도 서로 참조하거나 소유하는 구현이 많이 등장하는데, 다음 기준으로 구현했다.
  - 우선적으로 기본 생성주기를 같이하는 member variable 형태가 가능하면 사용한다.
  - 소유하지만 lazy loading이 필요한 member는 unique_ptr을 사용한다.
  - 소유하지 않지만 null이 불가능한 경우는 reference로 참조한다.
  - 소유하지 않지만 null이 가능해야 하는 경우는 raw ptr로 참조한다.
  
## scene
- 여러 node를 가리킨다.
- node들은 Tree 구조로 구성된다.
- node를 load할 때 시작점으로서 사용된다.

## node
- mesh를 소유
- skin은 소유하지 않고 참조한다.
  - 아직 쓰이지 않음.
- 다른 node들을 children으로 소유해서 tree형태로 참조하는 구조를 가진다.
  - root node가 모든 node를 소유하게 되는데 이 root node는 실재하지 않고 model에서 parent가 없는 node 모두를 소유한다.
  - 이렇게 구성한 이유는, 상위 node가 destruct 될때, 하위 children도 모두 destruct 되는 구조를 위해서다. cycle이 있거나 DAG 구조이면 구현이 좀 복잡해질텐데, 다행히 tree여서 간단히 구현했다.
- transform matrix정보를 가지고 있다. 이 transform은 parent를 기준으로 가져서 sceneGraph를 구성한다.
- node 구조는 mesh들 간의 관계나 skinning 등에 사용가능한 계층구조를 위한 abstraction으로 보면 될 것 같다.
  
## mesh
- 3d model의 mesh에 해당한다.
- 여러 primitive를 vector로 소유
- ubo 소유 
  - skinning을 위한 jointMatrice
  - NodeTransformMatrix
  - 이를 위한 buffer와 descriptorSet소유 
- vertex/index buffer는 model에서 소유하고, mesh는 primitive를 통해 index 정보만 가지고 있다.
  - model의 모든 vertex는 하나의 buffer로 관리되고, 각 mesh는 offset으로 접근하도록 해서 효율을 높인 것으로 보인다.

  
## primitive
- vertex/index offset and count
- material을 참조한다.
  - 소유는 model에서 소유한다.
- dimension
  - 모든 노드의 메쉬의 vertices의 좌표의 최대, 최소, center, radius 등의 값을 계산할 때 사용되는데, 아직 사용한 적은 없다.

## material
- 여러 texture를 참조한다. color/normal/metalic/occlusion/emissive...
  - texture의 소유도 역시 model에 있다.
- 하나의 descriptorSet을 가진다. 
  - 여러 texture의 image들은 set의 각 binding으로 들어간다.  

## texture
- 하나의 image 자원을 소유한다.
  - imageView를 image class에 추가해서 구현했다.
  - view와 VkImage의 분리가 필요한 경우가 생기면 분리하려 하는데 아직 찾지는 못했다.
  - mipmap 생성과 관련해서 view를 만들때 levelCount를 미리 알아야 하는 문제가 있었는데, 이 levelCount만 미리 지정해놓으면 이후 mip images의 내용은 변경해도 되는지 의문이 있었다.
    - 이런 생각이 든 이유는 이전 tutorial에서는 image를 먼저 생성하면서 mipmap 생성을 다 한 후, image view를 만들었다면
    - 이번에는 image view를 image와 같이 먼저 생성해놓고, image mipmap을 생성하려니 순서의 문제가 없는지에 대한 의문이었다.
    - 결론적으로 문제는 없었다. image view가 image access를 위한 handle 개념이므로 접근 영역에 대한 정보와 이미지의 내부 내용은 서로 독립적인 개념으로 이해했고, 다음 [명세 부분](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/VkImageViewCreateInfo.html#VUID-VkImageViewCreateInfo-subresourceRange-01718)을 참고했다.
- sampler를 소유한다.
- texture loader와 mipmap 생성을 위한 method를 가진다.


그외의 skin과 animation 관련된 구조는 아직 구현하지 않고 TODO로 남겨놨다. 이후 예제에서 추가할 계획이다.  

# Loading assets

model class에서는 각 자원들을 glTF file로부터 loading한다. 이후 그 자원들의 사용에 필요한 buffer와 descriptor set 등을 생성하고 초기화한다.  


## flags

[vgeu_flag.hpp](https://github.com/keechang-choi/Vulkan-Graphics-Example/blob/main/src/base/vgeu_flags.hpp)

glTF 구현에도 여러 flag의 사용이 필요했는데, vulkan-hpp에 구현된 template 형식을 참고해서 작성했다. template programming 관련 참고한 내용도 남겨두겠다.

- [https://github.com/KhronosGroup/Vulkan-Hpp/blob/main/vulkan/vulkan_enums.hpp](https://github.com/KhronosGroup/Vulkan-Hpp/blob/main/vulkan/vulkan_enums.hpp)
- [https://modoocode.com/295](https://modoocode.com/295)
  - SFINAE 라는 principle을 처음 알았는데, modern c++ 관련 기본적인 내용도 한번 정리할 필요성을 느꼈다.

## texture loading

glTF 내장된 image loading으로 파일에서 읽어온 image를 생성하고 mipmap 생성을 하는 내용이다. 원본 예제에서는 KTX format을 권장해서 이에 대한 구현이 들어있는데, 여기서는 우선 glTF 내장 texture 사용만 구현했다.

mipmap 생성과 관련해서는 tutorial에서의 방식과 유사한데 같은 결과를 내는 조금 다른 layout transition의 방식이 원본에 구현되어 있어서, 두 방식을 비교할 겸 좀 더 정리해봤다.  

두가지 비슷한 구조가 나와서 정리해두려한다.
- [ImageSubresourceLayers](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/VkImageSubresourceLayers.html)
  - buffer copy to image나 image blit에서 사용된다.
  - blit에서는 src/dst를 나눠서 2개가 사용된다.
  - 여러 layer를, 고정된 mipLevel에 대해 지정한다.
    - layer가 여러개인 image는 다루지 않았는데, [cube map](https://github.com/SaschaWillems/Vulkan/blob/master/examples/texturecubemap/texturecubemap.cpp)이 대표적인 예시다. skybox 구현에도 사용된다. 
- [ImageSubresourceRange](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/VkImageSubresourceRange.html)
  - pipeline barrier에서 image layout transition을 지정할 때 사용된다.
    - vgeu_utils.cpp에 구현된 `setImageLayout()` 내부에서 사용된다.
  - 여러 layer와 더불어, 여러 mipLevels를 지정한다.
    - buffer copy to image 전의 transition에서 사용될때는 0~mipLevels 전부 범위를 사용하지만,
    - mipmap generate에서의 transition에서는 , i번에서 1개씩 mipLevel 지정으로 사용한다.


이번에 구현할 방식에서는 mipmap generation은 흐름이 다음과 같다

- create mipLevels-count image by staging buffer
- transition: undefined → transfer dst: base 0, <o>count 1</o>
- CopybufferToImage: mipLevel 0
- <o>transition: transfer dst → transfer src : base 0, count 1</o>
- submit and flush(wait idle)
- mipmap generation for i in [1, mipLevels-1]
    - transition: <o>undefined → transfer dst: : base [i]</o>, count 1
    - blitImage using [i-1] → [i]
    - transition: <o>transfer dst → transfer src: base[i]</o>, count 1
- transition: <o>transfer src  → shader read only:  base 0, count mipLevels</o>

<style>
o { background-color: Orange }
</style>


이전 tutorial 에서 구현했었던 mipmap generation은 다음과 같다.  
> [Recap](../study-Vulkan-mipmap-multisampling#generating-mipmaps-1)

- create mipLevels-count image by staging buffer
- transition: undefined → transfer dst: base 0, count <o>mipLevels</o>
- CopybufferToImage: mipLevel 0
- <o>transition 안함</o>
- submit and flush (wait idle)
- mipmap generation for i in [1, mipLevels-1]
    - transition: <o>transfer dst → transfer src  : base [i-1]</o>, count 1
    - blitImage using [i-1] → [i]
    - transition: <o>transfer src→ shader read only: base[i-1]</o>, count 1
- transition: <o>transfer dst  → shader read only:  base [mipLevels-1], count 1</o>



차이를 정리해보면 다음과 같다.

|                 step                 |                     this example transition                      |                          past tutorial transition                           |
| :----------------------------------: | :--------------------------------------------------------------: | :-------------------------------------------------------------------------: |
|         첫 buffer copy 이전          |                 base mipLevel , undefined -> dst                 |                        전체 levels, undefined -> dst                        |
|        copy 후 iteration 이전        |                    base mipLevel , dst -> src                    |                                                                             |
| mipmap iteration for i=1~mipLevels-1 | [i] level, undefined -> dst <br> blit <br> [i] level, dst -> src | [i-1] level, dst -> src <br> blit <br> [i-1] level, src -> sharer read only |
|           after iteration            |               전체 levels, src -> shader read only               |                [mipLevels-1] level, dst -> shader read only                 |

최종 layout 들의 결과는 동일하다. 과정에서의 차이가 있긴한데, 성능상 비교는 하지 못했다.  
과거 tutorial에서의 방식이 command가 하나 적긴하다. 마지막 레벨의 변환은 src layout으로의 변환이 필요없어서 그 중간단계가 차이.  

## materials loading
- glTF material에 있는 texture index를 통해 load된 texture의 raw ptr을 const로 참조한다.
- 여러 종류의 texture중 있는 것들만 확인하여 전부 가져온다.
- 새로 생성된 material들은 model에서 vector로 소유해서 관리한다.

## nodes loading
- node는 tree 구조를 위해 recursive하게 loading 된다.
  - 한 node를 load하면 새로운 newNode를 local에서 unique_ptr로 생성한다.
  - child 정보를 recursive하게 모두 생성한다. 이때 parent로 newNode의 raw ptr을 전달한다.
  - mesh가 있는 node는 make_unique로 생성해서 소유한다.
  - 그 mesh의 primitives 정보도 make_unique_를 통해 소유하도록 생성한다.
  - 완료되면, newNode의 raw ptr은 model class의 멤버인 linearNodes에 저장한다. 
  - 그 newNode가 parent가 있으면 parent의 children에 move로 소유권을 넘겨 추가한다.
  - 그 newNode가 parent가 없으면 model class의 멤버인 nodes에 move로 소유권을 넘겨 추가한다.
- 결과적으로 linearNodes는 모든 node를 소유없이 참조하고,
- nodes는 root node들만 소유하게 된다.
- 그리고 각 node는 그 node의 childeren들을 모두 소유한다.

# draw
- model의 `draw()`는 모든 nodes를 돌면서 `drawNode()`를 호출해서 draw commands를 recording 한다.
- `drawNode()`는 tree traversal을 위해서 recursive하게 recording 된다. 
- `drawNode()` 내부에서는
  - 그 node가 소유한 mesh의 primitives를 돌면서 `vkCmdDrawIndexed()`를 호출한다. primitive의 index count와 first index가 사용된다.
  - 이때 texture 가 필요시, primitive가 참조한 material을 통해 bind DescriptorSets을 호출한다.


## pipelines
최종 결과를 확인하기 위해서, 세개의 pipeline과 그에 해당하는 shader를 작성한다.

- phong
  - 기본이 되는 pipeline이고, allow derivative flag를 통해 아래 두 pipeline 생성의 base가 되어 효율을 높인다.
  - [https://registry.khronos.org/vulkan/specs/1.3/html/chap10.html#pipelines-pipeline-derivatives](https://registry.khronos.org/vulkan/specs/1.3/html/chap10.html#pipelines-pipeline-derivatives)
  - shader는 blinn-phong lighting으로 구현했다.
  - ```glsl
    vec3 color = vec3(texture(samplerColorMap, inUV));

    // High ambient colors because mesh materials are pretty dark
    vec3 ambient = color * vec3(0.3);
    vec3 N = normalize(inNormal);
    vec3 L = normalize(inLightVec);
    vec3 V = normalize(inViewVec);
    vec3 R = reflect(-L, N);
    vec3 halfAngle = normalize(L + V);
    vec3 diffuse = max(dot(N, L), 0.0) * color;
    // vec3 specular = pow(max(dot(R, V), 0.0), 64.0) * vec3(0.35);
    vec3 specular = pow(max(dot(halfAngle, N), 0.0), 64.0) * vec3(0.35);
    outFragColor = vec4(ambient + diffuse + specular, 1.0);	
    ```
- toon
  - base pipeline과 다를게 없다. viewport의 경우 dynamic state로 지정했기 때문에, command buffer recording에서 변경해줄 수 있다.
  - shader는 다음과 같이 밝기 단계가 discrete 되도록 지정했다.
  - ```glsl
    vec3 N = normalize(inNormal);
    vec3 L = normalize(inLightVec);

    float intensity = dot(N, L);
    float shade = 1.0;
    shade = intensity < 0.80 ? 0.9 : shade;
    shade = intensity < 0.65 ? 0.75 : shade;
    shade = intensity < 0.35 ? 0.45 : shade;
    shade = intensity < 0.1 ? 0.15 : shade;

    outFragColor = vec4(inColor*shade, 1.0);	
    ```
- wireframe
  - rasterization state 의 polygon mode를 line으로 지정한다.

이 세가지의 pipeline을 `buildCommandBuffers()`에서 bindPipeline을 통해서 바꿔가며 각각의 draw와 호출하면 모든 로직의 구성이 완료된다.
이때 서로 화면 분할된 결과를 위해서, `setViewPort()`를 서로 다른 영역이 되도록 3분할 해주면 된다.  

이전부터 써오던 사과모델의 glTF format을 추가해서 다음과 같은 결과를 얻었다.
![image](/images/vge-pipelines-3.gif)

# TODO
현재 구현된 glTF는 pipelines 예제 구현에 필요한 것들 위주로만 작성해서 남겨둔 부분이 있다.

- texture 
  - base color texture 만 사용했는데, normal texture 및 다른 다양한 texture를 가진 material의 모델 추가.
- node hierarchy
  - 사용한 사과 모델이 단일 mesh여서, 이를 테스트 할 수 있는 계층구조 node의 glTF 파일 추가.
- animation
  - animation과 skinning에 해당하는 부분은 미구현했으므로 추가 구현.

다양한 glTF-sample은 다음 repo에서 얻을 수 있는데 저작권에 주의해야한다.  
[https://github.com/KhronosGroup/glTF-Sample-Models](https://github.com/KhronosGroup/glTF-Sample-Models)

참고로 해당 프로젝트에서 사용하는 모든 asset의 정보와 cc license는 [/assets](https://github.com/keechang-choi/Vulkan-Graphics-Example/tree/main/assets) 위치에 들어있다. 


