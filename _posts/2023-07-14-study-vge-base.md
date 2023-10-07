---
title: "Vulkan Graphics Examples - Base"
date: 2023-07-14T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-base-1.png
  thumbnail: /images/vge-base-1.png
---

이전 글에서 적은대로, vulkan tutorial에 대한 학습을 마치고, 예제 구현 중심의 학습 방향으로 전환을 했다.  
들어가기 전에, 어떤 내용들을 다룰 것인지와 repo 구성 환경에 대해서 정리해 놓으려 한다.  
그 후, 예제 코드 구조의 기본이 되는 base 구조에 대한 작업 내용과 첫번째 예제인 triangle rendering 예제 구현까지의 내용을 다루겠다.  

- [What's next?](#whats-next)
  - [Cloth simulation](#cloth-simulation)
  - [PBD - Position Based Dynamics](#pbd---position-based-dynamics)
  - [계획](#계획)
- [VGE repo 구성](#vge-repo-구성)
- [VGE - base](#vge---base)
  - [initVulkan](#initvulkan)
  - [prepare](#prepare)
  - [triangle](#triangle)
  - [interface](#interface)
    - [imGui](#imgui)
    - [CLI11](#cli11)
- [마무리](#마무리)

---

# What's next?
> [https://github.com/SaschaWillems/Vulkan](https://github.com/SaschaWillems/Vulkan) 

이 레포에 있는 여러 예제들을 실행시켜보고, 코드 구조를 훑어보면서, 앞으로 뭘 할지에 대해 생각해봤다. 예제 종류는 기본적인 내용과 glTF 모델, PBD, ray-tracing 등 다양한 주제가 있어서 처음부터 이 모든걸 공부하겠다고 잡으면 너무 주제가 넓어질 것 같아 우선 하나의 목적성을 두고 단계를 밟아가면서 살펴보려한다.  
그 중 마지막 tutorial 내용과 연결되기도 하고, 실행시켜봤을 때 흥미롭다고 느낀 내용이 compute shader와 simulation 부분이어서 해당 주제로 방향을 잡고 진행하기로 결정했다.   

## Cloth simulation
[(1) Unite 2016 - GPU Accelerated High Resolution Cloth Simulation - YouTube](https://www.youtube.com/watch?v=kCGHXlLR3l8)  
cloth simulation과 관련된 내용을 더 찾아보다가, Jim Hugunin 이라는 사람이 Unity 2016에서 발표한 영상을 보게 됐다.  
unity와 compute shader, real-time high resolution cloth simulation을 주제로한 발표인데, 내용을 정리하면 다음과 같다.  
- 당시 unity 내장 cloth simulation 내용은 cpu based 계산이기도 하고, resolution 관련 문제가 있었다.
  - 빠른 속도로 움직이는 물체와의 상호작용이 제대로 안됐음. fps 관련 한계로 인해서.
- 당시  Flex의 PhysX 에서 만든 엔진에서는 cloth simulation 이 GPU base로 동작했지만, Nvidia와 c++ 기반으로 구현돼어서 Unity C#에서 적용하면 최적화 문제가 있었다.
  - 결국 Flex의 물리엔진은 더 일반적인 물리 엔진이라 Cloth 특화된 engine을 자체 개발해서 좋은 성능을 냈다.
- demo 영상을 시연하며 영상이 마무리된다.
  - 관련해서 release한 프로그램도 있는 것 같은데, 유지 및 개발이 진행되고 있는 지는 모르겠다. [https://artfulphysics.com/](https://artfulphysics.com/)  
  
## PBD - Position Based Dynamics
simulation 관련해서 검색해보던 중 다음의 사이트를 찾았다.  
> [https://matthias-research.github.io/pages/tenMinutePhysics/index.html](https://matthias-research.github.io/pages/tenMinutePhysics/index.html)  

사이트 안에는, 논문과 유튜브 영상, lecture 자료, web simulation 등 볼 자료가 상당히 많았는데, 주로 Postion-Based Dynamics 라는 시뮬레이션 method에 눈이 갔다.  
아직 내용을 많이 살펴보진 않았는데, 간단하게 말하면 기존의 acceleration과 velocity등의 값들을 기반으로 한 Newton dynamics에서 벗어나서, position과 constraint를 기반으로 한 계산 방식을 사용하면, 여러 물리 현상을 좋은 효율로 계산하고 시뮬레이션 하기 적합하다는 내용으로 이해했다.  

tutorial 16에 해당하는 내용에서는, python + OpenGL + warp (Nvidia python GPU computation framework) 를 사용해서 해당 PBD의 기법이 GPU에서 계산하기에도 적합하다는 내용이 들어있다. 앞으로 주제 하나씩을 정해서 학습을 병행해서 Vulkan compute shader에대한 내용의 숙련도가 올라갔을 때, 작업을 시작하면 좋겠다고 생각했다.

## 계획

- tutorial 내용 반영 및 example 예제들 추가
  - base, triangle
  - pipelines, glTF model loading
  - animation, skinning
  - compute shader
- PBD 적용
  - cloth simulation
  - 혹은 흥미로워 보이는 simulation등
  - [https://www.youtube.com/watch?v=MgmXJnR62uA](https://www.youtube.com/watch?v=MgmXJnR62uA)
  - [https://www.youtube.com/watch?v=GjbcvqEOIuE](https://www.youtube.com/watch?v=GjbcvqEOIuE)

# VGE repo 구성
> [https://github.com/keechang-choi/Vulkan-Graphics-Example](https://github.com/keechang-choi/Vulkan-Graphics-Example)  

이전에 LVE와 tutorial을 공부할때는, desktop에 환경을 구성해놓고, wsl2 환경도 구성해서 ubuntu 환경에서 테스트도 할 겸 remote로도 실행했었는데, laptop으로도 내장 gpu를 사용하는게 성능이 더 좋아서 따로 환경구성부터 시작하기로 했다.
- lunarG에서 windows vulkan intall
  - 환경변수 등록, VK_SDK_PATH 확인
- glm, glfw 등 lib 설치 -> github submodule 활용으로 대체
- cmake install
- mingw C++ compiler install
  - visual studio 기반으로 작성하는게 windows에서 더 자주 보이긴 하는데, 향후 다른 platform 지원까지 고려하면 CLI 방식으로 컴파일하고 실행하는게 더 편해서 이렇게 하기로 했다.
  - 환경변수 MINGW_PATH 등록, Path에 bin 경로 추가
- cmake, subdir build 구조 구성
  - third-party 관리
  - glfw
  - glm
  - vulkan-hpp
  - imgui
    - imGUI 사용은 다음 guide를 참고했다. [https://vkguide.dev/docs/extra-chapter/implementing_imgui/](https://vkguide.dev/docs/extra-chapter/implementing_imgui/)
  
# VGE - base
가정 먼저 여러 example 예제들의 공통 내용이 될 base를 작성하고, 첫 예제인 trinagle rendering을 작성한 내용이다.

WIP

## initVulkan
## prepare
## triangle
![image](/images/vge-base-2.png)  
![image](/images/vge-base-3.png)  
![image](/images/vge-base-4.png)  
![image](/images/vge-base-5.png)  

## interface
[https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/1](https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/1)  
화면에 text를 표시하거나, user interface를 위해서 ImGuI라는 library를 사용했다. 여러 Graphics API와의 사용을 지원하고 간단하게 쓸 수 있는 장점이 있어보였다.
command line argument 는 따로 직접 구현하지 않고, CLI11 이라는 library를 추가했다.

### imGui
imGui vulkan example
> [https://github.com/ocornut/imgui/blob/master/examples/example_glfw_vulkan/main.cpp](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_vulkan/main.cpp)  


![image](/images/vge-base-1.png)

### CLI11
CLI11 examples
> [https://cliutils.github.io/CLI11/book/chapters/flags.html](https://cliutils.github.io/CLI11/book/chapters/flags.html)


![image](/images/vge-base-6.png)

# 마무리
