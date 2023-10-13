---
title: "[WIP] Vulkan Graphics Examples - Particles"
date: 2023-10-02T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-particle-42.png
  thumbnail: /images/vge-particle-ship.gif
---

compute shader 활용 예제를 base로, 이전에 tutorial에서 작성했던 것 보다 더 다양한 효과 구현에 목표를 뒀다.
먼저 particle 간의 gravity simulation을 작성한 후, particle dream 예제를 구현해보는 방향을 잡았다.

> [https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/4](https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/4)


- [Motivation](#motivation)
- [Prerequisites](#prerequisites)
  - [numerical integration](#numerical-integration)
  - [mesh attraction](#mesh-attraction)
- [Plan](#plan)
  - [작업 순서](#작업-순서)
  - [CLI11 and ImGui](#cli11-and-imgui)
- [Progress](#progress)
  - [synchronization](#synchronization)
    - [memory barrier](#memory-barrier)
  - [particle rendering](#particle-rendering)
  - [particle-calculate-integrate](#particle-calculate-integrate)
    - [pipeline 구성](#pipeline-구성)
    - [shader 구성](#shader-구성)
    - [specialization Constants](#specialization-constants)
    - [fix](#fix)
  - [two-body simulation and verification](#two-body-simulation-and-verification)
  - [trajectory](#trajectory)
    - [line drawing](#line-drawing)
  - [physics and numerical integration](#physics-and-numerical-integration)
    - [integration method 비교](#integration-method-비교)
- [mesh attraction](#mesh-attraction-1)
  - [interaction](#interaction)
    - [ray-casting](#ray-casting)
  - [triangle uniform distribution](#triangle-uniform-distribution)
    - [work group size](#work-group-size)
  - [skinning in compute shader](#skinning-in-compute-shader)
    - [Recap: mesh and skin](#recap-mesh-and-skin)
  - [trajectory in GPU](#trajectory-in-gpu)
- [Demo](#demo)
- [마무리](#마무리)

---

# Motivation

- n body gravity simulation
  - [SaschaWillems/Vulkan-computenbody.cpp](https://github.com/SaschaWillems/Vulkan/blob/master/examples/computenbody/computenbody.cpp)
  - 기본 틀은 위 예제를 따라가며 작성할 계획이다. 이전 보다 조금 더 복잡한 계산이 compute shader에서 실행되는 만큼, shared memory 사용 및 compute pipeline 구성과 syncrhonization에 초점을 맞췄다.
- 아래 자료들은 모두 particle dreams 예시의 내용을 다루는데, webGL로 작성된 것들은 demo를 브라우저에서 실행해볼 수 있게 되어 있어서 실행해보며 어떤 기능들을 넣을지 구상할 수 있었다.
  - [Particle Dreams (karlsims.com)](http://www.karlsims.com/particle-dreams.html)
  - [A Particle Dream | Nop Jiarathanakul (iamnop.com)](https://www.iamnop.com/works/a-particle-dream)
  - [https://github.com/byumjin/WebGL2-GPU-Particle](https://github.com/byumjin/WebGL2-GPU-Particle)
- animation in compute shader
  - 이전 예제에서 animation 계산을 (정확히는 animation update는 cpu에서 하고, 계산된 joint matrices를 활용한 skinning계산을) vertex shader에서 실행했는데, 이번 예제 구현에서는 vertex shader 이전 단계에서 모든 animation이 완료된 animated vertices data가 SSBO형태로 필요하다. 
    - 이 animated vertices를 target으로 particle이 attraction 되는 효과를 만들 계획인데, 자세하게는 이 particle을 수치 적분하기 이전의 calculate compute shader에서 이 자료가 사용될 예정이다.
    - 이를 위해서 비슷한 자료를 찾아보던 중 다음의 rust로 작성된 vulkan viewer 예제에서 구조를 참고했다.
  - [rustracer/crates/examples/gltf_viewer/shaders/AnimationCompute.comp at main · KaminariOS/rustracer (github.com)](https://github.com/KaminariOS/rustracer/blob/main/crates/examples/gltf_viewer/shaders/AnimationCompute.comp)

# Prerequisites
## numerical integration
particle의 움직임을 나타나기 위해 처음 직관적인 접근은 뉴턴 역학을 활용하는 것이다. position을 update 하기 위해서, velocity를 사용하고, velocity를 update하기 위해서 acceleration을 사용하는 방식이다.  
acceleration은 우리가 지정해준 force에 따라서 계산된다.
이전까지에는 각각이 미분-적분 관계를 가진다는 기본적인 생각으로 단순하게 시간 간격 dt만 알고 있다면, 적분을 근사해서 원하는 최종 값을 얻을 수 있겠다고 생각했다. (가속도에 dt를 곱해서 속도에 누적시키고, 속도에 dt를 곱해서 위치에 누적시키는 방식)
하지만 이 dt는 fps에 영향을 받기도 하고, 계산량이 많아진다면 간격이 커지면서 오차가 커질 수 밖에 없다. 그리고, 이 누적된 오차는 global error를 만드는데, 이 error에 따라서 원하는 simulation과 전혀 다른 simulation이 나올 수도 있다. 
그래서 이 관련된 수치 적분에는 다양한 기법이 존재하는데, 처음 직관적인 방식을 `Euler method`라고 한다.  
이 Euler method 보다 차수를 높여서, 더 적은 오차를 갖게 하는 방식도 있는데, 여기서는 더 확장된 Runge-Kutta method에 대한 내용을 알면, 나머지는 그 특수한 경우로 볼 수도 있다.
- [Euler method](https://en.wikipedia.org/wiki/Euler_method)
- [midpoint method](https://en.wikipedia.org/wiki/Midpoint_method)
- [Runge-Kutta method](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods)
  - 관련 구현 자료: [https://smath.com/wiki/GetFile.aspx?File=Examples/RK4-2ndOrderODE.pdf](https://smath.com/wiki/GetFile.aspx?File=Examples/RK4-2ndOrderODE.pdf)

error estimation의 order이외에도, 수치 적분의 방식에따라 여러 특성을 가지는데, 아래 문서의 설명들을 보고 개념을 많이 참고 했다.
> [https://adamsturge.github.io/Engine-Blog/mydoc_updated_time_integrator.html](https://adamsturge.github.io/Engine-Blog/mydoc_updated_time_integrator.html)  

그중 `symplecticity` 라는 개념이 있는데, 이는 energy conservation과 관련된 개념으로, simulation의 장기적 결과에 큰 영향을 준다. 
위의 각 method의 order에 대응되는 method는 다음과 같다고 볼 수 있다.
- [symplectic-Euler method](https://en.wikipedia.org/wiki/Semi-implicit_Euler_method)
- [Stoermer-Verlet method](https://en.wikipedia.org/wiki/Verlet_integration)
- [fourth-order symplectic method](https://en.wikipedia.org/wiki/Symplectic_integrator#A_fourth-order_example)

해당 내용을 좀 더 이해해보려고, 수학 공부를 조금 다시 해보기도 했는데, Textbook 하나를 잡고 진득하게 공부할 필요가 있을 것 같다. 관련 키워드는 남겨놓겠다.
- ODE(Ordinary Differential Equations). 관련 주제로 검색했을때는, Ernst Hairer 교재가 많이 나오긴 했다.
- numerical integration
- Hamiltonian mechanics 
  - 깊게 다루기보다는 주로 numerical integration을 적용할 할 예시들이 역학들이고, 수치 적분에서는 미분방정식을 evaluation해야하니 같이 나오는 것 같다.
  - Lagrangian mechanics, calculus of variations
- symplectic integration
  - flow, differential form
  - differntial geoemtry관련 내용도 알면 이해하기 좋아보였다.

우선적으로 공부를 할 수는 없을 것 같고, 생각날때 조금씩 알아가야할 것 같아 symplectic function에 대한 개념까지만 공부했다. (integration method가 symplectic한 개념은 아직 자세히 보지 못했다.)  
어쨌든 해당 내용을 공부하지 않더라도, 검색해서 찾은 방식들대로 integration을 구현하면, 에너지가 보존되는 효과를 누릴수 있다.

## mesh attraction
model의 mesh attraction에도 위의 수치 적분은 동일하게 적용된다. 단지 evalation하는 과정이, n-body simulation에서는 O(n^2) 이지만, mesh attraction에서는 미지 지정한 mesh의 vertice로 attract되도록 지정해주면 된다. (나는 attraction에 공기 저항 처럼 drag에 해당하는 force를 추가해줬다.) 여기서부터는, 물리 simulation이 아니라 특수 효과를 구성한다는 생각으로, 적절한 coefficient 조절을 통해 현실성은 고려하지 않고 보이는 것에만 집중해서 구현할 계획이다.   

한가지 짚고 넘어갈 점은, model의 vertices 뿐만 아니라, 그 면적 자체에도 attraction이 되도록 구현하는 점이다. 이 부분을 복잡하게 생각했었는데, 다른 구현 코드들을 보니 단순히 particle 개수를 추가해서, 남는 particle들을 mesh의 내부 분할 점으로 attract 시키는 방식을 쓰고 있어 나도 그 방식을 채택했다.  
이때 쓰이는 테크닉이 삼각형 내부의 uniform한 random point를 생성하는 것인데, 아래 글을 참고해서 작성했다.  

> [https://math.stackexchange.com/questions/18686/uniform-random-point-in-triangle-in-3d](https://math.stackexchange.com/questions/18686/uniform-random-point-in-triangle-in-3d)  
> 
> $$
> \displaylines{
>   \begin{aligned}
>      & r_1 \sim U(0, 1) \\ 
>      & r_2 \sim U(0, 1) \\ 
>      & w_1 = \sqrt{r_1} * (1-r_2) \\ 
>      & w_2 = \sqrt{r_1} \\ 
>      & triangle \; ABC \\ 
>      & p = A + w_1 * (B-A) + w_2 * (C-A)
>   \end{aligned}
> }
> $$  
> 위의 방식으로 계산된 random variable p는, 삼각형 ABC 내부의 uniform distribution을 따르게 된다.

이 좌표를 target으로, particle들이 attract되게 만들면, model의 mesh를 채우게 될 수 있을 것이다. attract되는 정도, particle의 수, 크기, 색상 등을 조정할 옵션을 만들고, mouse click 을 통한 interaction을 추가하는 것 까지가 계획이다.  

# Plan

## 작업 순서
- graviti n-body simulation 구현
  - integration method를 여러 방식을 option으로 선택할 수 있도록 구현 후 비교
  - 구현 후, 2-body simulation의 analytic 한 solution 과 비교해서, 옳게 simulation 되는지 검증.
    - 확인을 위한 particle의 trajectory rendering 기능 구현
  - particle 개수를 늘려서 성능확인.
- model attraction 구현
  - model SSBO 구현 후, dynamics 없이 정지된 particle 위치 확인.
  - skinning in compute shader 작성
    - pipeline 및 synchronization 고려
  - model 선택 기능 추가.
- 이 예제를 완료 후
  - PBD 방식에 대한 예제 구현.
    - cloth simulation도 좋을 것 같다. animation과 상호작용할 수도 있음.
  - [Publications (matthias-research.github.io)](https://matthias-research.github.io/pages/publications/publications.html) 
  - CPU vs. GPU (naive) vs. GPU (PBD) 계산 성능 비교
    - collision 관련 예제를 만들어 봐도 좋겠다는 생각이 듦.  
  
## CLI11 and ImGui
구현하면서 command line argument와 ImGui을 통한 옵션 선택을 적극적으로 추가했다. 처음에 단순한 초기 설정들은 CLI11을 통해 구현했고, 이후 복잡한 선택이 필요한 값들은 ImGui widget을 추가해서 구현했다.  
상수로 박아뒀던 값들 중에서 변경이 자주 필요하거나 실험이 필요한 값들 위주로 옵션으로 변경했다. 일부 변수들은 자원 생성과 관련되어서 초기화 과정이 필요한 것들이 있는데, 이런 값들은 재시작을 통해 반영되도록 따로 표시해서 재시작 버튼을 활용할 계획이다. 재시작은 가장 편한 방법이 생성한 모든 instance를 파괴하고 새로 생성하는 것이어서 재시작 loop를 추가했다.  

두 방식을 모두 쓰는 값도 있어서 코드의 일관성이 조금 깨진 측면도 있지만, 앞서 밝힌대로 엄격하지 않게 해당 기능들을 필요시 편하게 사용했다.

# Progress
## synchronization

> [https://vkguide.dev/docs/gpudriven/compute_shaders/#compute-shaders-and-barriers](https://vkguide.dev/docs/gpudriven/compute_shaders/#compute-shaders-and-barriers)  

이전 tutorial에서 compute shader를 다룰때는, fence를 사용해서, compute shader의 계산을 host에서 기다린 후, 다음 단계 (이미지 얻어오고 draw하는 과정)를 진행했다.  
여기서는 다른 방식으로 synchronization을 구현하는데, pipeline barrier를 사용하는 방식이다. (필요한 이유는 제출된 command들이 submit order로 시작하지만 완료 순서는 모르기 때문)  
pipeline barrier에 SSBO buffer memory barrier를 사용해서 execution/memory dependency를 구성해준다.
### memory barrier

- in a queue
  - 위에서 간단히 설명한 pipeline barrier
- two queue
  - 이전 예제와의 차이점이 또 존재하는데, compute dedicated queue family의 사용이다.
  - 이전에는 하나의 queue에서 compute와 graphics 작업을 모두 수행했다면, 이번에는 compute 목적의 queue family에서 다른 queue를 하나 더 생성했다.
  - pipeline barrier에는 이를 위한 기능이 있는데, `Queue ownership transfer` 개념이다.
- 기본적인 설명은 다음을 참고 했다.
  - [https://www.khronos.org/blog/understanding-vulkan-synchronization](https://www.khronos.org/blog/understanding-vulkan-synchronization)
  - 서로 다른 두 queue family index의 queue가 하나의 자원(buffer나 image)를 공유할 때, memory access에 synchronization을 제공.
  - 일반적인 pipeline barrier와의 차이점으로 src stage와 src access mask는 src queue쪽에, dst stage와 dst access mask는 dst queue쪽에 제출된다는 점이다.
- 자세한 설명은 spec 문서를 참고하면 된다.
  - [https://registry.khronos.org/vulkan/specs/1.3/html/vkspec.html#synchronization-queue-transfers](https://registry.khronos.org/vulkan/specs/1.3/html/vkspec.html#synchronization-queue-transfers)
  - 자원을 생성할 때, `VkSharingMode`를 `VK_SHARING_MODE_EXCLUSIVE`로 지정한 경우는 명시적으로 queue family 간의 ownership을 옮겨줘야 한다.
  - 두가지 부분 release / acquire 과정으로 구성되는데, 
    - release
      - pipeline barrier가 제출하는 queue가 src queue family index에 해당한다.
      - dst access mask는 무시된다. visibility operation이 실행되지 않는다. 
      - release operation은  availability operation이후에 실행되고, second synchronization scope의 연산들 이전에 실행된다.
    - acquire
      - pipeline barrier가 제출하는 queue가 dst queue family index에 해당한다.
      - 이전에 release한 자원의 영역과 일치해야 한다.
      - src access mask가 무시된다. availability operation이 실행되지 않는다.
      - acquire operation은 first synchronization scope의 연산들 이후에 실행되고, visibility operation 이전에 실행된다.
    - 그리고 이 release와 acquire 연산들은 알맞은 순서에 실행되도록 app에서 semaphore등의 사용을 통해 execution dependency를 지정해야 한다고 한다.
- 예시
  - [https://github.com/KhronosGroup/Vulkan-Docs/wiki/Synchronization-Examples#transfer-dependencies](https://github.com/KhronosGroup/Vulkan-Docs/wiki/Synchronization-Examples#transfer-dependencies)
  - transfer 과정에서 이후에 사용할 queue의 family index가 다른 경우는 Queue ownership transfer를 수행해주고 있다.
  - [https://stackoverflow.com/questions/60310004/do-i-need-to-transfer-ownership-back-to-the-transfer-queue-on-next-transfer](https://stackoverflow.com/questions/60310004/do-i-need-to-transfer-ownership-back-to-the-transfer-queue-on-next-transfer)
    - 위 예시에 해당하는 질문글이다.
    - 



## particle rendering
![image](/images/vge-particle-0.png)  
![image](/images/vge-particle-1.png)  
![image](/images/vge-particle-2.png) 

## particle-calculate-integrate

### pipeline 구성

### shader 구성

gl_GlobalInvocationID

gl_LocalInvocationID

![image](/images/vge-particle-3.png)  
![image](/images/vge-particle-4.png)  
![image](/images/vge-particle-5.png)  


![image](/images/vge-particle-2.gif) 

![image](/images/vge-particle-6.png)  
![image](/images/vge-particle-7.png)  
![image](/images/vge-particle-8.png)  
![image](/images/vge-particle-9.png)  

### specialization Constants


[Template argument deduction - cppreference.com](https://en.cppreference.com/w/cpp/language/template_argument_deduction#Non-deduced_contexts)

### fix
shader numParticles

[https://registry.khronos.org/OpenGL-Refpages/gl4/html/barrier.xhtml](https://registry.khronos.org/OpenGL-Refpages/gl4/html/barrier.xhtml)


[https://registry.khronos.org/OpenGL-Refpages/gl4/html/memoryBarrier.xhtml](https://registry.khronos.org/OpenGL-Refpages/gl4/html/memoryBarrier.xhtml)


## two-body simulation and verification
[https://evgenii.com/blog/two-body-problem-simulator/](https://evgenii.com/blog/two-body-problem-simulator/)


![image](/images/vge-particle-10.png)  
![image](/images/vge-particle-11.png)  
![image](/images/vge-particle-12.png)  
![image](/images/vge-particle-13.png)  

## trajectory
![image](/images/vge-particle-14.png)  
![image](/images/vge-particle-15.png)  
![image](/images/vge-particle-16.png)  
![image](/images/vge-particle-17.png)  
![image](/images/vge-particle-18.png)  

### line drawing
![image](/images/vge-particle-20.png)  


## physics and numerical integration
### integration method 비교

![image](/images/vge-particle-23.png)  
![image](/images/vge-particle-24.png)  
![image](/images/vge-particle-25.png)  
![image](/images/vge-particle-26.png)  
![image](/images/vge-particle-27.png)  
![image](/images/vge-particle-28.png)  


# mesh attraction
![image](/images/vge-particle-47.png)  

## interaction
![image](/images/vge-particle-model.gif)

### ray-casting
## triangle uniform distribution

![image](/images/vge-particle-48.png)  

![image](/images/vge-particle-29.png)  
![image](/images/vge-particle-30.png)  
![image](/images/vge-particle-31.png)  
![image](/images/vge-particle-32.png)  
![image](/images/vge-particle-33.png)  
![image](/images/vge-particle-34.png)  
![image](/images/vge-particle-35.png)  
![image](/images/vge-particle-36.png)  

### work group size
## skinning in compute shader
### Recap: mesh and skin


![image](/images/vge-particle-37.png)  
![image](/images/vge-particle-38.png)  
![image](/images/vge-particle-39.png)  
![image](/images/vge-particle-40.png)  
![image](/images/vge-particle-41.png)  
![image](/images/vge-particle-42.png)  
![image](/images/vge-particle-43.png)  
![image](/images/vge-particle-44.png)  

## trajectory in GPU
![image](/images/vge-particle-19.png)  

![image](/images/vge-particle-21.png)  
![image](/images/vge-particle-22.png)  

![image](/images/vge-particle-45.png)  
![image](/images/vge-particle-46.png)  
# Demo
 
  
![image](/images/vge-particle-animation.gif)  


# 마무리

PBD


