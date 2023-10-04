---
title: "Vulkan Tutorial - Generating mipmaps & MultiSampling"
date: 2023-05-19T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vulkan-tutorial-mipmap-2.png
  thumbnail: /images/vulkan-tutorial-mipmap-2.png

---

Mipmap과 MultiSampling에 관한 내용도 이전 little vulakn game engine tutorial 에서 한 번 다뤘던 주제들이다. 개념들을 정리하고 넘어가려 한다.

최근에 tutorial을 끝내고 예제들을 구현해보는 단계로 넘어가면서, 내용 정리를 제대로 하지 않았다. 빠르게 넘어가서 새로운 예제들 구현에 속도를 붙이려는 생각이 있었는데, 다시 복습하는 느낌으로 정리하고 확실히 하지 않고 넘어간 부분들은 좀 더 조사해서 정리해놓으려 한다.


- [Generating Mipmaps](#generating-mipmaps)
  - [Intro](#intro)
  - [Image Creation](#image-creation)
  - [Generating Mipmaps](#generating-mipmaps-1)
  - [Linear filtering support](#linear-filtering-support)
  - [Sampler](#sampler)
  - [mipmap 적용 예시](#mipmap-적용-예시)
- [MultiSampling](#multisampling)
  - [Intro](#intro-1)
  - [Available sample count](#available-sample-count)
  - [Setting up a render target](#setting-up-a-render-target)
  - [Adding new attachments](#adding-new-attachments)
  - [Quality improvements](#quality-improvements)
- [마무리](#마무리)


---


# Generating Mipmaps
[vulkan-tutorial.com 해당 내용](https://vulkan-tutorial.com/Generating_Mipmaps)


## Intro
mipmap 생성을 추가하는 내용이다. vulkan에서는 우리가 직접 mipmap을 어떻게 생성할 건지에 대한 컨트롤을 전부 제공한다.
mipmap이란, 간단하게는 미리 계산된 축소된 이미지다. (어원은 라틴어로 작은 공간에 더 많다는 뜻이라고 한다) 구체적 단계(LOD: Level of Detail) 개념을 위해서 사용되는데, 각 단계마다 이미지의 크기를 절반으로 줄여놓은 mipmap을 사용해서 카메라 기준 멀리있는 물체의 texture를 sampling할때는 더 작은 sampler mip image를 사용하는 원리이다. 장점으로 렌더링 속도를 높이고, Moire pattern이 생기는 걸 방지할 수 있다.  

어차피 멀리 있으면 결국 화면에 보여지는 크기가 작아지고, 물체 안의 픽셀 수도 작아지므로 필요한 resolution도 낮아진다. 자연스럽게 한 screen pixel안에 들어가는 texel의 수도 많아지게 될텐데 큰 크기의 texture를 사용할 필요가 없어진다.  

정리하면, 물체와 카메라 사이의 거리가 가변적일때, mipmap을 사용해서 적당한 크기의 texture를 사용하게되면 다음과 같은 장점을 얻을 수 있어 자주 사용되는 기법이다.
- 멀리 있는 곳에서 발생하는 aliasing 효과 제거 (이 aliasing이 Moire pattern을 발생시킴)
  - screen의 해상도가 texture의 detail을 보여주기에 충분히 높지 않은 경우인 undersampling의 상황, 모든 display에는 해상도 한계가 있기때문에 어쩔수 없다.
  -  더 좋은 모니터를 쓰거나 MSAA 기법을 써도 되는데, 거리가 멀어진 물체를 표현할때만 이런 방식을 적용할 수는 없다. 이때 mipmap을 써서 texture의 해상도를 낮춰버리면 aliasing 현상을 없앨 수 있다. 
- 큰 사이즈 대신 적절한 사이즈의 texture를 사용함으로써 cache effieciency를 높인다.

## Image Creation
Vulkan에서는 이런 다른 mip level의 mip image들을 하나의 `VkImage`에 저장한다. 0 level을 original 이미지로 하고, 그 다음 레벨의 작은 이미지들의 mip chain을 직접 생성해서 저장할 수 있다.  

`VkImage`를 생성할 때 총 mipLevels가 몇개인지 명시해줄 수 있는데, 지금까지 이 argument를 1로 지정해왔다. 이를 적절한 크기로 바꾸고 이와 관련된 다음 부분들을 수정해야 한다.
- createImage()
- createImageView()
- transitionImageLayout()

https://github.com/keechang-choi/Vulkan-Game-Engine-Tutorial/commit/9443485e77792f6ffe09f10abf191336cbcd9da6

## Generating Mipmaps

이제 texture image에 여러 mip levels로 지정하여 생성하는 것은 완료했지만, 그 내용을 채워주지는 않았다. 기존의 staging buffer를 통해 transfer해주는 건 mipLevel 0의 original image에만 적용이 된다.

나머지 level의 이미지는 어떻게 채워줘야할까? `vkCmdBlitImage()`라는 command를 통해 채워넣을 수 있다. 이 command는 copy, scaling, filtering등을 지정해서 수행해준다. (blit: block of data를 옮기거나 copy)

이 연산을 각 레벨별로 호출해서 내용을 채우면 되는데, 이때 주의할 점이 몇가지 있다.
- 이 blit 연산은 `vkCmdCopy`와 같이 transfer operation에 해당하므로, 이미지를 생성할때, image usage를 trasfer src와 dst 모두 지정해줘야 한다.
- 이미지의 layout도 transfer src optimal과 dst optimal을 지정해줘서, general인 layout보다 성능을 높이자.
  - 기존에 텍스쳐 이미지 생성시 두었던 transition을 제거하고 mipmap 생성시에서 구현.

generateMipmaps()의 로직은 다음과 같다
- command buffer recording 시작.
- i = 1부터 level iteration을 시작
- pipeline barrier로 i-1 level의 layout을 transfer dst optimal -> src optimal로 지정하고, access mask는 trasfer write -> read로 지정한다. stage mask는 transfer -> transfer(이전 blit 연산과 초기 staging copy가 끝나게 기다린 후 새로운 blit을 준비시키는 역할)
- blit command로 i-1 level -> i level을 채운다. 이때 blit src/dst offset을 mip 크기에 맞게 지정.
- pipeline barrier로 i-1 level의 layout을 transfer src opt -> shader read only opt로 바꿔서 fragshader에서 읽을 준비, access mask는 transfer read -> shader read, stage mask는 transfer -> frag shader로 전환한다.
- mip크기를 절반으로 줄이고 이를 지정한 i=levels-1까지 반복한다. (지정할 레벨은 이미지 크기의 log_2 값으로 미리 지정)
- iteration이 끝나고, 마지막 mipLevels - 1 의 pipeline barrier를 수행한다.
- single Time command로 이를 제출한다. 


## Linear filtering support

device별로 linear filtering을 blit시에 지원하지 않는 경우도 있다고 한다. device에서 지원하지 않으면, format 변경을 통해 linear blitting을 지원하는 texture image format을 찾거나, 애초에 image loader에서 stb image resize 등으로 mipmap generating을 구현 할 수 있다.  
실제로 적용할때 runtime에 mipamp을 생성하는 경우는 거의 없다고 한다. 미리 생성해서 texture file에 저장을 해놓는 것이 일반적이기 때문이며, base level 0에 여러 level의 이미지를 한번에 넣어놓는 경우도 있다고 한다.  
3D model format인 glTF 포맷을 찾아보다가 알게된 내용인데, KTX라는 [Khronous Texture](https://www.khronos.org/ktx/) format에서는 이 mipmap levels에 맞게 이미지를 저장해놓고 불러올 수 있는 기능이 있는 것 같다. (나는 아직은 이 format을 사용하지 않고 일반 png나 jpg로 텍스쳐를 불러온 다음 위처럼 직접 mipmap generating 하는 로직으로만 glTF format을 사용해본 상태다.)


## Sampler

mipmap 데이터는 준비가 됐고, sampler에서 이 데이터를 어떻게 읽을지에 대한 지정도 필요하다.  
minLod, maxLod, mipLodBias등이 그 값인데, 이것들을 미리 지정해놓으면, sampler가 적절한 lod를 정해서(두 level의 결과를 blend하기도 하고) rendering에 사용한다고 한다. 이때 sampled point의 screen size 등을 고려해서 계산되도록 API 내부적으로 구현이 되어 있다는 것 같다.   
sampler에 지정해놨던 magFilter와 minFilter중 어떤것을 사용할지도 이 정해진 LOD값을 참고해서 결정되는데, camera로부터 멀리 있는 물체는 LOD값이 크게 되어 minFilter가 사용되고, 가까이 있는 경우는 LOD값이 작게되며 0인 경우는 magFilter를 사용하게 된다.

## mipmap 적용 예시

참고한 tutorial에서 사용된 viking room 모델을 두개를 띄워놓고, 좌측은 mipmap없이, 우측은 mipamp 적용하여 카메라와 거리를 다르게 해봤다.

|     left without mipmap, right with mipmap     |
| :--------------------------------------------: |
| ![image](/images/vulkan-tutorial-mipmap-1.png) |
| ![image](/images/vulkan-tutorial-mipmap-2.png) |
| ![image](/images/vulkan-tutorial-mipmap-3.png) |

멀어질수록 LOD에따른 mipmap의 사용 효과가 나타난다. generate시 linear filtering을 사용했기때문에 우측 물체가 blur 된 것 같은 효과를 보인다.


# MultiSampling

[vulkan-tutorial.com의 해당 내용](https://vulkan-tutorial.com/Multisampling)

## Intro
이제 LOD for texture가 가능해져서 물체가 카메라에서 멀어짐에따라 더 부드러워진 이미지를 확인 가능했다. 근데 렌더링된 이미지를 확대해보면 지그재그한 edge부분이 나타나는 경우들은 별개의 문제로 남았다.  

![image](/images/vulkan-tutorial-msaa-1.png)

이런 효과를 aliasing이라고 지칭했는데, 렌더링에 사용가능한 픽셀의 수 (screen의 해상도)가 한정되어 있기 때문에, 모든 디스플레이에서 확대해보면 나타날 수 밖에 없다.
- oversampling이 texture 의 detail이 부족해서 나타나는 현상이라면 undersampling은 screen의 detail이 부족해서 나타나는 현상이라고 정리했다.   
이 geometry의 edge에서 발생하는 aliasing은 screen의 pixel 한계 때문에 발생하는 undersampling이라고 볼 수 있다. (물체에 가까이 갔을때 texture 해상도가 낮아서 깨져보이는 oversampling과는 구분된다고 이해함.) screen 해상도가 높았다면 이런 계단 현상을 줄일 수 있었을 것이지만, 우리는 다른 해결법으로 MSAA(Multi Sampling Anti Aliasing)을 여기서 다룬다.
- 이 기법을 직관적으로 보여주는 이미지가 tutorial에 제공되어 있다.
- 일반적인 렌더링에서 픽셀의 색은 single sample point로부터 결정되는데, 대부분의 경우 그 점은 center of the target pixel on screen이다. 특정 선이 한 픽섹은 통과하면서 그 sample point를 포함하지 않으면 blank로 처리되면서 계단 효과가 발생한다.
  ![image](https://vulkan-tutorial.com/images/aliasing.png) *[https://vulkan-tutorial.com/images/aliasing.png](https://vulkan-tutorial.com/images/aliasing.png)*
- MSAA는 이 sample point를 여러개를 써서 최종색을 결정하는 방식이다. 더 좋은 결과의 이미지를 얻지만 계산상 비용이 더 든다. 그래서 app에 따라서 최대의 sample count를 쓰는게 performance 를 고려했을때 최선의 선택은 아닐 수 있다.
  ![image](https://vulkan-tutorial.com/images/antialiasing.png) *[https://vulkan-tutorial.com/images/antialiasing.png](https://vulkan-tutorial.com/images/antialiasing.png)*


## Available sample count

하드웨어가 얼마나 많은 sample point를 지원하는지 알아보자. 보통 현대 GPU는 최소 8개 이상을 지원한다고 한다.   
physicalDeviceProperties에서 볼 수 있는데, depth buffer도 쓰고 있으니, color와 depth sample count를 모두 고려해야 한다.  

![image](/images/vulkan-tutorial-msaa-2.png)

https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/VkSampleCountFlagBits.html

## Setting up a render target

MSAA에서 각 픽셀은 먼저 offscreen buffer에서 sampled 된 후, 화면으로 render된다.  
이 새로운 buffer는 렌더링 하고 있던 regular images와 약간 다른데, 각 픽셀당 하나 이상의 샘플을 저장해야 하기 때문이다.
multiSampled buffer가 생성되고 나며느 기존 default framebuffer로 resolved 되어야 한다.  
이를 위해서 새로운 render target을 생성해야 하는데, depth buffer 처럼 추가해주면 된다.  
tutorial에서는 depth buffer 처럼 in-flight frames 별로 하나씩이 아니라 공용으로 하나의 자원만 있으면 된다고 하는데, 이 부분에 확실치 않은 부분이 있어서 나는 각 in-flight frames 별로 하나씩 생성했다.
 > https://stackoverflow.com/questions/62371266/why-is-a-single-depth-buffer-sufficient-for-this-vulkan-swapchain-render-loop  
 > 하나의 depth buffer만 사용하는 부분도 정확히 이해가 되지 않아서 좀 더 찾아보고 있는데, 각 frames in flight 별로 만드는게 확실한 방법 같다. 공용 자원으로 쓸 경우, subpass dependency를 추가하면 된다고 하는데 굳이 여기서 그렇게 구현할 필요는 없을 것 같다. resources & synchronization 관련해서 개념이 부족한 것도 있고 tutorial 특성상 자세하게 다루지 않는 부분들도 꽤 있는 것 같아 다음 포스트에서 다른 자료들과 함께 정리하고 넘어가려 한다.  

 createResource()에서 기존 1로 되어있던 numSamples를 지정할 수 있도록 추가하자. 그리고 depth image 들도 msaaSamples 수와 같도록 업데이트 해야 한다.  

 https://github.com/keechang-choi/Vulkan-Game-Engine-Tutorial/commit/2a1ef5b44d495a7192c8028c679bac20445c38e5

## Adding new attachments

렌더패스 생성 부분의 info를 수정한다. 그리고 기존 colorAttachment의 finalLayout을 present가 아니라, color attachment opt로 바꾼다. 이는 multiSampled된 이미지는 직적 present 할 수 없으므로,resolve하는 과정을 추가할 것이기 때문.  
그 후 frameBuffer에서도 attachemnt를 업데이트 하고 (index 주의), pipeline 생성에서도 msaaSamples를 가져쓰도록 변경하자. (device로부터)

https://github.com/keechang-choi/Vulkan-Game-Engine-Tutorial/commit/1f83d84cdf569d3f972030b5550f15e901cf6725

|                 without MSAA                 |                  with MSAA                   |
| :------------------------------------------: | :------------------------------------------: |
| ![image](/images/vulkan-tutorial-msaa-3.png) | ![image](/images/vulkan-tutorial-msaa-4.png) |
| ![image](/images/vulkan-tutorial-msaa-5.png) | ![image](/images/vulkan-tutorial-msaa-6.png) |

## Quality improvements

shader aliasing에 의한 잠재적 문제를 해결하지 않았다고 한다. -> geometry의 edge만 smoothing 해주고 있고 interior filling에 대한건 안다뤘기 때문.  
polygon은 smooth하면서, 내부 texture에 대비되는 색이 클 경우는 문제가 나타날 수 있다고 하고, sample shading을 적용하면 성능 감소는 있을수 있지만 해결된다고 함.

현재 예시에서는 뚜렷한 변화가 안보여서 우선 더 이상 자세히 찾아보지는 않았다.

--- 

# 마무리

이제 vulkan-tutorial.com의 내용을 전부 다뤘다. extra-chapter인 compute shader가 있긴 한데, 그전에 resource와 synchronization 등을 좀 더 다루고 정리한 다음 compute shader를 다룬 후 이 tutorial 을 끝내려 한다.

이후에는 [Sascha Williems의 Vulkan Example](https://github.com/SaschaWillems/Vulkan) 레포의 예제들을 보면서 하나씩 구현해보거나 그 구조를 바탕으로 구현하고 싶은 내용들을 다뤄보려 한다.   

compute shader 관련해서는 우선 extra-chapter에서 기본적인 것들을 다룬 후, [Metthias Mueller의 PBD(Position Based Dynamics)](https://matthias-research.github.io/pages/index.html)의 자료를 보고 적용해보고자 하는 생각이 있다.