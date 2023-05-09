---
title: "Vulkan Tutorial - Depth buffering & Loding models"
date: 2023-05-10T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vulkan-tutorial-depth.png
  thumbnail: /images/vulkan-tutorial-depth.png

---

이전 little vulakn game engine tutorial 을 따라오면서 대부분 이미 작성했던 내용들.
가볍게 강조할 것들만 정리해놓고자 함.  

- [Depth buffering](#depth-buffering)
  - [Intro](#intro)
  - [3D geometry](#3d-geometry)
  - [Depth image and view](#depth-image-and-view)
  - [Explicitly transitioning the deoth image](#explicitly-transitioning-the-deoth-image)
  - [Render pass](#render-pass)
    - [subPass ?](#subpass-)
  - [Frame buffer](#frame-buffer)
  - [Clear values](#clear-values)
  - [Depth and stencil state](#depth-and-stencil-state)
  - [Handling window size](#handling-window-size)
- [Loading models](#loading-models)
  - [Intro](#intro-1)
  - [Library](#library)
  - [Sample mesh](#sample-mesh)
  - [Loading vertices and indices](#loading-vertices-and-indices)
  - [Vertex deduplication](#vertex-deduplication)


---


# Depth buffering
[vulkan-tutorial.com 해당 내용](https://vulkan-tutorial.com/Depth_buffering)

![image](/images/vulkan-tutorial-depth.png)  

## Intro
이전에 사과 모델을 띄웠을때, 위 이미지처럼 face들이 가까운 것과 먼것에 대한 처리 없이 나왔어야 하지만, 이전 과정[(Fixed Function Pipeline Stages -Vulkan Game Engine Tutorial 04)](https://youtu.be/ecMcXW6MSYU?list=PL8327DO66nu9qYVKLDmdLW_84-yE4auCR)에서 이미 depth test에 대한 처리가 구현되어 있어 잘 나올 수 있었다.
depth test란 간단히 현 시점 기준 보이는 가까운 것은 그리고 가려지는 먼 것은 그리지 않게 하기위한 테스트이다.

## 3D geometry
vulkan-tutorial.com/Depth_buffering 의 내용에서는 이전 texture 내용을 2d flat 사각형에 그렸기 때문에 2d vertex 을 사용했었다.

[Euler Angles & Homogeneous Coordinates - Vulkan Game Engine Tutorial 12](https://www.youtube.com/watch?v=0X_kRtyVzm4&list=PL8327DO66nu9qYVKLDmdLW_84-yE4auCR&index=14) 에 해당하는 내용이며, 다음 세가지를 2D에서 3D에 맞게 변경하는 내용이다.
- attribhuteDescription에서 3으로 바꿔줘야 함.
- vertex shader
- model vertices
  
이 단계를 마치고 렌더링 했을 때, 위와 같은 앞뒤가 뒤죽박죽인 화면을 얻을 수 있다. 

depth 처리를 위한 두가지 방법을 소개하는데, 
- draw call 순서를 조정
- depth test를 사용 (depth buffer)
  
1번 방법은 투명한 물체 표현에 사용된다 (order independent transparency는 해결하기 힘든 문제라고 하는데, 그래서 이전의 point light 의 semi-transparent 구현에서도 alpha blending과 order dependent한 방식으로 해결했다.)

[Alpha Blending and Transparency - Vulkan Game EngineTutorial 27](https://www.youtube.com/watch?v=uZqxj6tLDY4&list=PL8327DO66nu9qYVKLDmdLW_84-yE4auCR&index=31)

여기서는 2번 방법에 대한 구현이 진행된다. 원리는 rasterizer 단계에서 fragment를 생성할때마다, depth test를 실행해서 새로운 fragment가 이전 것 보다 가까운지 depth 값을 비교해서 가까운 것만 저장하는 방식이다.

주의할 점은 OpenGL에서는 -1 ~ 1 이 기본 depth 범위이지만, Vulkan에서는 0 ~ 1 이기에 변경을 해줘야 한다.



## Depth image and view

depth data도 image기반이며, swap chain 생성시 명시적으로 생성을 해줘야 한다.
기존 image 생성 처럼 다음 세가지를 생성해야한다.
- image
- memory
- image view

stencil component가 있는데, stencil test에 사용된다고 한다. 아직 다루지 않아서 넘어가려하는데, potal rendering 등에 쓰일 수 있다고 한다. [https://en.wikipedia.org/wiki/Stencil_buffer](https://en.wikipedia.org/wiki/Stencil_buffer )  

그리고 이 stencil buffer를 사용할 경우 image format이 달라지기 때문에 유의.

## Explicitly transitioning the deoth image

render pass에서 image layout을 depth attachment로 transition해주기 때문에 명시적으로 작성할 필요 없다고 한다. 하지만 안내대로 추가해주었다. (실수로 잘못 추가하면 validation layer warning을 보게된다.)

아직 render pass나 compatibility 개념에 대해 잘 모르는 부분이 많아서 관련 문서를 나중에 읽어봐야겠다.
[Vulkan® 1.1.249 - A Specification (with all registered Vulkan extensions) (khronos.org)](https://registry.khronos.org/vulkan/specs/1.1-extensions/html/chap8.html#renderpass-compatibility)

만들어 놓은 depth 관련 자원들은 frame buffer 생성시 attachment를 통해 설정된다.

stage관련,  depth buffer reading은 early fragment test stage(rasterization 이후, fragment shader 이전 단계)에서 일어나고, writing(새로운 fragment가 test통과 후 그려질때 write)은 late fragment test stage에서 일어난다고 한다. transition의 dst stage는 당연하게 둘 중 더 이른 것으로 설정했다.



## Render pass

depth attachment description을 설정해야 한다.
renderPass가 pipeline의 청사진 같은 개념이기에 실제 들어올 데이터와 같은 format을 명시해줘야 한다.

- format : depth image foramt과 동일하게
- attachment load op : clear 사용 (clear value도 변경해줘야 함)
- stor op : dont care로 지정해서 하드웨어 차원에서 최적화 할 수 있도록 둔다.
- init layout / final layout : transition에서 명시해준 layout 들이 여기서 지정해줬기 때문에 불필요했던 것 같은데 render pass 관련 개념을 좀 더 알게되면 보충하겠다.

### subPass ?
기존에 있던 subPass의 color attachment에 추가로 depth attachment를 추가해준다. subpass에 대해서 다루진 않았던 것 같아서 skip한 내용을 좀 더 찾아봤다. [https://vulkan-tutorial.com/Drawing_a_triangle/Graphics_pipeline_basics/Render_passes](https://vulkan-tutorial.com/Drawing_a_triangle/Graphics_pipeline_basics/Render_passes)  

- 하나의 renderPass는 여러개의 subPass로 이뤄질 수 있다.
- subPass는 뒤따라오는 렌더링 연산인데, 이전 패스들의 frame buffer 내용에 의존한다.
  - 예를 들어 post-processing 효과들의 sequence
  - 이런 연산들을 하나의 renderPass에 묶으면 좋은점이, vulkan이 알아서 순서를 바꿔서 메모리 bandwidth를 conserve해서 성능을 높여준다고 한다.
- 각 subPass는 하나 이상의 attachment를 참조한다.
- attachment reference의 attachment 설정으로 shader의 location과 연결지어준다.
- 다른 attachment 예시들
  - pInputAttachments : shader에서 읽을 것
  - pResolveAttachments:  color att의 Multi Sampling에 사용될 것
  - pDepthStencilAttachment: depth와 stencil
  - pPreserveAttachments: 이 subpass에서 사용안되지만 보존되어야 할 데이터
  - 등등

기존 하나 있던 subPass의 color attachment는 여러개가 가능하지만 depth는 하나의 attachment만 가능하다고 한다.

dependency와 이를 사용할 renderPassInfo를 수정해준다.
- dependency mask에는 stage와 access 지정을 하는데, early fragment test stage와 write access로 지정을 해준다
- clear를 하는 load operation이 있기때문에 write로 지정해줘야 한다.

## Frame buffer

만들어둔 depth image view를 attachment에 추가해준다.

지금 구현상태와 차이점이 있는데, color attachment는 swap chain image마다 다르지만, depth image는 공용으로 쓰일 수 있다고 한다.
subpass가 하나여서 그렇다고 하는데, 지금 구현에서는 color와 마찬가지로 in-flight image 수 만큼 나눠져 있다. 추후 추가할 부분을 고려해서 나눠놓은 것인지 모르겠으나 좀 더 살펴볼 필요가 있어보인다.

## Clear values

현재 구현 코드에서는 `beginSwapChainRenderPass`에 구현된 내용이며, clear value로 color에 추가로 depth,stencil 초기값을 지정해준다.
vulkan에서 가까운 depth value가 0.0f이고 먼 값이 1.0f이기에 초기값은 1.0f로 지정해주는 것에 유의.
clear value 순서도 당연하게 attachment index와 일치해야 한다. (*color : 0, depthStencil : 1)

## Depth and stencil state

이제 depth attachment를 사용할 준비가 끝났다.  
pipeline 생성시 config에 depth test enable 등 사용 설정을 명시한다.
- depthTestEnable
- depthWriteEnable
- depthCompareOp
- depthBoundsTestEnable
- stecil buffer 관련은 우선 안씀

맨 위의 이미지는 이 설정을 꺼놓고 실행시켜 재현했다.


## Handling window size

swap chain recreate시, 변경된 화면 extent등을 맞게 depth 자원도 새로 재생성해줘야 한다

# Loading models
![image](/images/vulkan-tutorial-loading.png)  

## Intro
저장된 model file에서 읽어오는 것
이미 [Loading 3D Models - Vulkan Game Engine Tutorial 17](https://www.youtube.com/watch?v=jdiPVfIHmEA&list=PL8327DO66nu9qYVKLDmdLW_84-yE4auCR&index=20) 에서 동일한 내용을 다뤘다.

## Library

tiny obj loader 사용
직접 loader를 간단히 만들어도 되지만, 어차피 실용적인것이 아니라서 불러온 데이터를 활용하는 것에 집중한다.

## Sample mesh

[Sketchfab](https://sketchfab.com/) 사이트에서 모델을 찾기 좋다고 한다.
tutorial과 동일한 viking room 모델을 사용했다.

## Loading vertices and indices

`vkCmdBindIndexBuffer` 시 index type을 명시해주는데, 이전에 65535개 보다 작았어서 `uint16_t` 를 사용하던 것에서 `uint32_t`로 변경해준다.

obj file의 face를 통해서 vertices reuse가 가능하다. 

`tinyobj::LoadObj` 에서는 기본으로 `triangulate` arg가 true로 되어 있는데, obj file format은 삼각형 face이외의 도형도 가능하긴 하지만 우리는 삼각형만 사용.

- 각 face는 vertices array를 포함
- 각 vertex는 (position, normal, texture)의 indices를 포함
- material과 texture per face도 포함할 수 있으나 우선 안씀.

모델의 vertices 수가 많아짐에 따라 컴파일 시 -O3 옵션 또눈 Release 모드를 사용하라고 한다.

texture coordinate을 읽을 때, obj format 과 vulkan format의 vertical 이 반대인 것 유의. 
obj에서 0은 이미지의 bottom, vulkan에서의 0은 이미지의 top.  



## Vertex deduplication

모델의 vertices 자체에 중복이 많다면 index buffer의 장점을 살리지 못할 수 있다.
이런 경우를 위해서 hash map을 활용한 중복 제거를 추가한다.

이때 hash에는, position, color, normal, uv의 vector들을 combine해야 하는데, 이 문제가 간단하지 않다고 한다.

이 문제가 아직 완벽한 solution이 있는게 아니라서 c++ 공식 버전에 포함되지 않은 것이라는 말도 있던데, tutorial에서는 [cppreference.com](https://en.cppreference.com/w/cpp/utility/hash)의 예시 방식을 추천하지만 우리 구현은 [https://stackoverflow.com/questions/2590677](https://stackoverflow.com/questions/2590677)(boost 구현 방식)을 참고하여 구현되어 있다. 
애초에 boost lib의 많은 기능들이 c++ standard로 추후에 포함되곤 하니 신뢰할 순 있을 것 같다.

--- 
boost 에서 쓰고 있는 magic number? (`0x9e3779b9`) 방식과 xor 방식의 차이인 것 같은데 이 hash combine 내용만 한번 따로 다뤄봐도 재밌겠다고 생각이 들었다.  
그나저나 effective c++ / effective modern c++ 책을 사놓고 잘 안읽고 있는데 틈틈이 봐야겠다.