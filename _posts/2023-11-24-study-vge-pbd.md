---
title: "[WIP] Vulkan Graphics Examples - PBD"
date: 2023-11-24T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-pbd/vge-pbd-1.png
  thumbnail: /images/vge-pbd/vge-pbd-1.png
---

Position Based Dynamics관련 내용들을 습득하고, 예제들을 구현해보기로 했다. lecture에는 영상과 구현 자료가 잘 정리되어 있고, 논문 및 course note 등 정확한 정보가 충분해서 공부하기 좋았다.  
이론과 관련되어서는, 이전부터 조금씩 봐왔던 것들 중 자세히 짚고 넘어가지 못한 내용들을 정리하려 한다. numerical integration과 hash 관련 내용들이 그렇다.  
일부는 예시들을 그대로 구현한 것 도 있고, 일부 Vulkan 활용에 편하도록 수정한 것들도 있는데, 아직은 GPU 활용한 예제를 다루지 않고 CPU base의 간단한 simulation위주로 작성했다.  

> [https://matthias-research.github.io/pages/tenMinutePhysics/index.html](https://matthias-research.github.io/pages/tenMinutePhysics/index.html)


> [https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/5](https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/5)

- [PBD: Position Based Dynamics](#pbd-position-based-dynamics)
  - [Integration Method](#integration-method)
- [Lectures \& Plan](#lectures--plan)
- [Simulations](#simulations)
  - [Compute animation](#compute-animation)
  - [2D simulation setup](#2d-simulation-setup)
  - [Cannon ball](#cannon-ball)
  - [Ball collision - naive](#ball-collision---naive)
  - [Beads on wire](#beads-on-wire)
    - [Constraint dynamics](#constraint-dynamics)
  - [Triple pendulum](#triple-pendulum)
  - [SoftBody](#softbody)
    - [XPBD](#xpbd)
    - [Interaction](#interaction)
  - [Neighbor search](#neighbor-search)
    - [Spatial hash](#spatial-hash)
    - [hash function](#hash-function)
  - [Collision by constraint](#collision-by-constraint)
- [마무리](#마무리)

---

# PBD: Position Based Dynamics

> [https://matthias-research.github.io/pages/publications/PBDTutorial2017-CourseNotes.pdf](https://matthias-research.github.io/pages/publications/PBDTutorial2017-CourseNotes.pdf)

이론적인 내용은 위의 survey 자료를 읽고 정리하는 것으로 진행했다. 다 읽진 못해서 계속 병행해서 읽으면서 정리하려 한다.  
전통적인 real-time simulation 분야에서 쓰이던 impulse나 force 기반의 접근의 문제점을 제시한다. [real-time rendering](https://en.wikipedia.org/wiki/Real-time_computer_graphics)을 달성하기 위해서는 성능이 매우 중요한데, 실시간으로 사용자와 상호작용이 필요하면서도, 끊어지지 않는 속도로 매 frame의 계산이 완료되어야 하기 때문이다. 영화 인터스텔라의 블랙홀 장면을 렌더링하기 위해서 사전에 몇백시간의 분량을 고성능 컴퓨터로 물리학자들과 협업해서 계산했다는 글을 본적이 있는데, 그것과 대비된다.  
force 기반 방식에서 주로 사용하는 간단한 mass-spring model에 있어서도, 여러 문제점이 있었다.
- spring network를 구성하는 방식에 따라 물체의 행동이 달라짐
- spring constant를 조정하는 것이 어려움
- mass spring network로는 부피 보존 효과를 구현하기 힘들다.  

이에대한 단점을 개선하는 방식이 Position 기반 방식 `PBD` 이라고 제시한다.
근본적인 방식은, 힘이나 속도를 변경하는 간접적인 방식이 아니라, 위치 자체를 제약조건을 만족하도록 직접 수정하고, 속도는 그에따라 업데이트 해주는 방식이다. 제약조건을 다뤄야하기 때문에, [Constraint Dynamics](https://graphics.pixar.com/pbm2001/pdf/notesf.pdf)의 내용이 자주 등장한다. 예전에 봤던 물리엔진 관련 영상이 이와 같은 자료를 기반으로 하고 있어서 남겨놓겠다.

![](https://www.youtube.com/watch?v=TtgS-b191V0)


`PBD`의 전체적인 알고리즘은 다음처럼 설명한다.  
[https://matthias-research.github.io/pages/tenMinutePhysics/09-xpbd.pdf](https://matthias-research.github.io/pages/tenMinutePhysics/09-xpbd.pdf) 의 설명을 참고해서 디테일은 조금 다를 수 있다.
- 초기화. position, velocity, inverse mass
  - mass의 역수를 자주 써서 inverse mass로 관리한다. +inf의 mass 표현이 0으로 가능해니다.
- time loop
  - 모든 vertices에 대해서
    - 속도에 force계산을 통한 가속도 누적
      - force 계산에는 x를 사용
    - 위치에 속도 누적
      - 이전 위치 x를 p에 임시 저장
      - x에는 속도를 누적한 새로운 내용 저장
  - 모든 vertices에 대해서 충돌 제약 생성
    - 위치 업데이트로 인해 발생된 충돌 검출
  - 모든 제약 조건에 대해서 (지정한 제약과 위의 충돌 제약 포함)
    - 제약조건 projection 혹은 solve
      - x에 delta x를 직접 반영해서 업데이트
  - 모든 vertices에 대해서
    - v를 (x-p)/dt로 업데이트
  - 속도 update
    - 여기서 충돌 등으로 인해 추가적으로 필요한 속도 처리를 해주는 것 같다.

이와 같이 알고리즘이 간단하고, 병렬화하기 좋은 구조로 되어있는 것이 장점이다. constraint solve에서는 iterative한 method를 쓰는 것 보다, dt 자체를 substep으로 쪼개서 수행하는 것이 결과가 좋다는 실험 결과도 제시한다.  
이 알고리즘의 correctness나 convergence rate 혹은 error approximation 등에 대해서 생각해보려면, time integration 관련 내용이 등장하는데, 주요 키워드는 다음과 같다.  
- implicit Euler method
  - abstract에서 제약 준수와 연관된 implicit Euler method의 variational formulation이라고 소개함.
- Verlet method
  - integration scheme이 비슷하다고 하면서 다른 method와 비교를 제시하고 있음
- Symplectic Euler method
  - prediction step에서 사용됨. (v를 x 보다 먼저 업데이트)
- implicit backward Euler method
  - constraint force를 반영하는 방식에서 사용됨
  - constrained minimization으로 볼 수 있음. 
  - first order 방식 뿐 아니라 second order method도 가능함.

numerical integration 관련해서는 이번 기회에 못본 내용들을 좀 더 자세히 정리하고 넘어가려 한다.



## Integration Method
> [https://adamsturge.github.io/Engine-Blog/mydoc_midpoint_method.html](https://adamsturge.github.io/Engine-Blog/mydoc_midpoint_method.html)


- Euler method
- implicit Euler method
  - (backward)
- Semi-implicit Euler method
  - Symplectic Euler method
- Mid-point method
- Verlet method

# Lectures & Plan

> [Ten Minute Physics (matthias-research.github.io)](https://matthias-research.github.io/pages/tenMinutePhysics/index.html)

![](https://www.youtube.com/watch?v=oPuSvdBGrpE)

영상 렉쳐는 시작점으로 보고 가기 좋다. 다루는 내용은 다음과 같이 이 순서대로 나도 따라가려한다.  

- PBD 기반 지식
- 2D particles
- constraint - beads, pendulum
- Soft Body - XPBD
  - spatial hashing
- cloth
- GPU
  - atomic add,
  - jacobi solver, Gauss Seidel
  - graph coloring
- fluid

우선 GPU를 사용한 연산을 다루기 이전까지는 모두 CPU 기반의 시뮬레이션들을 구현해보면서, PBD 원리나 구조를 이해하는데 중점을 두려한다.  
그래서 해당 예시들을 구현할 수 있는 code base를 하나로 묶어서 다양한 예제 구현을 우선적으로 진행 했고, 이후 정리된 구조를 만들어갈 계획이다.  

# Simulations
## Compute animation

우선 이전까지 작성했던 예제들 중 앞으로 필요할 것 같은 내용을 정리했다. 먼저 compute shader에서 animation을 미리 계산하는 것은 이후 cloth interaction등에서 사용될 수 있을 것 같아 코드를 수정하고 시작했다.  


floor를 추가하고 animation을 확인했다. empty texture를 checker board로 설정했다.

|  |  |
| :---: | :--- |
| ![image](/images/vge-pbd/vge-pbd-2.png) | ![image](/images/vge-pbd/vge-pbd-3.png) |


이전 particle 예제에서와 조금 다른 점은, 초기 transfer 부분이 필요치 않아 제거한 점이다. 그에따라서 queue ownership transfer도 잘 맞춰줘야하며, 잘못된 사용시 아래와 같은 validation layer의 error 메세지를 볼 수 있다.  
```
validation layer: Validation Error: [ UNASSIGNED-VkBufferMemoryBarrier-buffer-00004 ] Object 0: handle = 0x17d413d6c00, type = VK_OBJECT_TYPE_COMMAND_BUFFER; | MessageID = 0x991fd38f | vkQueueSubmit(): in submitted command buffer VkBufferMemoryBarrier acquiring ownership of VkBuffer (VkBuffer 0xad19770000000122[]), from srcQueueFamilyIndex 0 to dstQueueFamilyIndex 2 has no matching release barrier queued for execution.
```

animation 적용시, 다른 모델들은 모두 문제가 없었는데, ship 모델에만 문제가 있어서 확인해본 결과, compute dispatch에서 실수가 있었다. 원인은 dispatch시 model vertex count를 제대로 맞추지 않았던 것이었다.  
이외에도 buffer alignment나, skinning시 node hierarchy, 등에서 잘못된 부분은 없나 체크하며 다음 단계로 넘어갔다.

![image](/images/vge-pbd/vge-pbd-4.png)

## 2D simulation setup

![image](/images/vge-pbd/vge-pbd-5.png)

floor와 animation을 정리한 이후에는, 2D simulation을 추가해줄 사각형 frame과, 단순한 원과 같은 2D geometry model 들을 생성할 수 있는 구조를 추가했다.  
lighting 관련해서는 기존의 point light 하나를 그대로 유지했는데, 필요시 point light를 추가하거나 directional light와 함께 사용해도 좋을 것 같다.  
우선은 2D simulation에는 lighting의 별도 적용 없이 단색으로 표현되도록 설정했다.

## Cannon ball

![image](/images/vge-pbd/vge-pbd-6.png)
단순히 중력에 영향을 받아 움직이는 2d ball이다. 벽과의 충돌만 처리했다.

## Ball collision - naive
![image](/images/vge-pbd/vge-pbd-7.png)
단순한 방식의 collision 처리이다.
ball 들이 서로 충돌했을 때 mass를 고려한 충돌을 처리했다.  
충돌 검출이 단순한 방식의 O(n^2) 이기 때문에 많은 수의 ball을 처리할 수 없는 한계가 있다.  


## Beads on wire
![image](/images/vge-pbd/vge-pbd-8.png)

원형 wire에 구슬 beads가 껴있는 상황에 대한 시뮬레이션이다.  ball끼리의 충돌은 이전 예제와 동일하다. 추가된 점은 ball이 원형 wire위에 있도록 유지되는 것인데, 이 현상을 쉽게 묘사하는 방법이 제약조건을 활용한 constraint dynamics이다. 

아래는 이 제약조건을 활용한 시뮬레이션과 직접 수식을 풀어서 계산한 analytic 한 solution의 비교장면이다.
![image](/images/vge-pbd/vge-pbd-9.png)


![image](/images/vge-pbd/vge-pbd-bead-analytic.gif)

처음에는 붉은색(analytic solution)과 파란색(simulation) 결과가 동일하게 움직이지만 오차가 점차 커지는 것을 볼 수 있다.  
여러 방법으로 이 오차를 줄일 수 있는데, substep 수를 늘리는 방식으로 간단하게 해결 가능하다.  


렉쳐에서는 제약조건 달성을 위한 세가지 기존의 방법을 설명하고, 우리가 사용할 PBD 방식의 해결법이 이 문제들을 어떻게 처리하는지 설명한다.  
- spring을 활용
  - stiffness를 조정해야하는 문제가 있고, 큰 stiffness는 numerical problems를 일으킨다.
- generalized coordinates
  - 원운동을 해야하면 polar coordinates로 모든 위치 계산에 사용되도록 설정해서 아예 움직임을 제한하는 방법이다.
  - 계산이 복잡해지는 문제가 있다.
  - 참고 사이트를 추천. [https://myphysicslab.com/](https://myphysicslab.com/)
- constraint force를 푸는 방법
  - velocity를 constraint manifold에 tangential하게 만드는 방법이라고 한다.
  - 초기값이 만족되어야 하고, drift와 관련된 문제가 있다고 한다. 
  - 자세한 내용은 다음의 constraint dynamics에 나와있다.


PBD 적용된 방식을 요약하면 다음과 같다.
- bead가 not on wire이면 wire로 옮긴다.
- velocity도 그 옮겨준 위치를 사용해서 update한다.
  - 복잡한 calculus나, 힘과 가속도 계산, drift fixing 등의 과정이 필요없다.
  - constraint force를 간접적으로 계산해낼 수도 있다.
- substep을 사용해서 정확도를 높일 수 있다.
  - substep을 늘리면 결국 한번의 업데이트에 사용되는 dt가 작아지게 되면서 수치들이 precision 범위 밖으로 내려갈 수도 있게 된다. 모두 float (16bytes)의 값을 사용하다가, 이 예제부터 double을 사용하도록 수정했다.
- analytic solution과 비교해서, PBD의 방식이 정답에 converge하는 것을 확인 가능하고, constraint force등의 수치도 비교가능하다.


### Constraint dynamics
[https://graphics.pixar.com/pbm2001/pdf/notesf.pdf](https://graphics.pixar.com/pbm2001/pdf/notesf.pdf)

geometric constraints (일정 거리를 유지해야 한다던가, 원운동을 해야한다던가)를 만족하면서 물리적 법칙을 따르는 운동을 하도록 하는 것이 목표인 내용이다.  
이를 위해서 constraint force를 직접 계산해서 particle의 가속도를 legal하도록 변환하는 작업을 수행한다.  
결국 constraint 만족을 위해 힘과 가속도에 초점을 맞추는 방식인 반면 PBD는 위치에 초점을 맞춘다고 보면 될 것 같다. 
사용되는 용어느 notation이 유사한 것이 많아 한번 읽어보면 PBD 이해에도 도움이 된다.  

![image](/images/vge-pbd/vge-pbd-17.png)

## Triple pendulum

여기서는 hard constraint와 PBD 적용에 대해서 다룬다.  
- 일정 거리가 유지되어야 함
  - stiffness가 무한인 spring으로 볼 수 있다.
  - cloth not stretch나 hair, robot arms 등에 유용하다.
- stiff spring 은 stiffness 튜닝이 필요하고, 클 경우에는 numerical problems의 문제가 있다.
  - 그래서 constraint force를 쓰는 방법
    - 두 입자 사이의 선에 수직인 방향으로만 움직이도록 constraint force를 줘서 거리를 유지시키는 개념.
    - drift problems를 해결해야한다.
  - generalized coorindates를 쓰는 방법
    - x1, x2 대신, middle x와 각도 alpha를 쓰면, by construction으로 제약조건 만족이 가능해지지만 수식이 복잡해진다.
  - PBD 방식

PBD 방식에서는 x를 먼저 constraint를 만족하는 위치로 옮긴다.  
이때 질량에 반비례하는 weight를 줘서 constraint를 반영한다. 
벽에 고정된 묘사는 질량을 무한으로 주면 된다. (질량의 역수를 0으로 설정)  
XPBD라는 확장된 방식에 대해서도 언급하는데, soft constraint에서는 accuracy를 높여주지만 hard constraint에서는 차이가 없다고 한다.  

아래는 triple pendulum의 hard constraint를 PBD 방식으로 구현한 과정이다.  



| image | explanation |
| :---: | :--- |
| ![image](/images/vge-pbd/vge-pbd-10.png) | 기본적으로 필요한 값들은 pos, vel, mass, length, theta, omega, prePos이다. <br> 붉은색은 비교를 위한 analytic한 solution이다. |
| ![image](/images/vge-pbd/vge-pbd-11.png) | particle 사이에 line을 추가해준 형태이다. line은 하나의 동일한 직선 모델을 transformation만 바꿔가며 보이도록 설정했다. 이제 좀 pendulum같아 보인다.  |
| ![image](/images/vge-pbd/vge-pbd-12.png) ![image](/images/vge-pbd/vge-pbd-14.png) | particle의 움직임을 보기위해, tail(혹은 trail, trajectory)를 추가한 모습이다.  <br> 이전 particle 예제에서 초기에 구현했던 방식과 유사하게 구현했는데, 모든 시뮬레이션이 CPU 기반이기도 하고 particle수가 많지 않아 단순한 방식으로 CPU에서 계산한 tail을 mapped buffer에 memcpy하는 방식으로 구현했다. |

particle 수를 옵션에서 늘릴 수 있게 했는데, 다음과 같은 결과가 나온다.

| | | |
|:-:|:-:|:-:|
|![image](/images/vge-pbd/vge-pbd-16.png) | ![image](/images/vge-pbd/vge-pbd-13.png) | ![image](/images/vge-pbd/vge-pbd-15.png) | 




## SoftBody
sofybody lecture를 확인하면, 3d model에 대해서 tetrahedorn(사면체)의 부피를 보존하는 제약조건을 주어 이를 구현한다.  
제약조건은 크게 두가지인데, 다음과 같다.
- 사면체의 각 edge들의 길이 보존
- 사면체의 부피 보존

lecture의 코드에서는 이 모델과, 부피보존을 위한 사면체 정보를 모두 제공하는데, 이 데이터가 어떻게 구성되었는지는 이후에 다루기때문에, 나는 2D sofybody와 triangle을 이용해서 구현하기로 결정했다.  

| image | explanation |
| :---: | :--- |
| ![image](/images/vge-pbd/vge-pbd-18.png) | 초기 sofybody의 구조를 구현하고, 중력에 의한 이동을 확인했다. |
| ![image](/images/vge-pbd/vge-pbd-19.png) | 초기 constraint를 만족 시키도록 위치를 수정해주어서, soft circle이 collapse 되는 현상이 구현된 것을 확인했다. 아직 길이와 부피 제약조건에 들어가는 계수(compliance 혹은 stiffness)를 결정하지는 않았다.   |
| ![image](/images/vge-pbd/vge-pbd-20.png) | soft circle이전에 더 간단한 polygon을 구현해서, 길이와 부피 제약조건의 적당한 계수들의 역할을 확인했다. |
| ![image](/images/vge-pbd/vge-pbd-21.png) | blender 를 활용해서 2D soft circle에 쓰일 object를 작성했다. |
| ![image](/images/vge-pbd/vge-pbd-22.png) | 구현된 soft circle의 모습이고, 아직 collision은 구현되지 않았기에 두 softbody가 겹쳐진 모습이다. |

### XPBD

lecture 중간에 XPBD(Extended Position Based Dynamics)를 설명해주면서, 다른 방법들과 비교해주는 내용을 정리해봤다.

- force based
  - 관통으로 발생한 겹친 거리와 stiffness 계수를 사용해서 충돌을 처리한다.
  - force -> velocity -> position 순으로 변경된다.
  - reaction lag이 존재한다.
  - stiff한 처리를 위해서 계수를 키우면 stability 문제와 overshooting 문제가 생긴다.
    - 이 stiffness를 어떻게 정해야 하는지도 문제다.
  - k를 작게해서 squish한 system을 만들 수 있다.
- impulse based simulation
  - 관통은 detection 에만 사용된다.
  - separating velocity가 따로 있고, impulse 개념으로 이 수치를 정한다.
  - 더 stable하고, velocity update를 통제할 수 있어서 overshooting 문제가 없다.
  - velocity만 사용하는 방식이기에, drift 문제가 발생한다. 이를 해결하기 위한 별도의 테크닉이 필요.
- PBD
  - 관통은 detection에만 사용됨.
  - position을 직접 바꿔서 overlap을 없앤다.
  - 그 후 dynamics를 위한 velocity update
  - position을 통제하기 때문에, 조건없이 stable하다.
  - drift 문제가 없다.
  - PBD는 integrator와 solver를 합친 개념이다.
  - constraint solve를 여러 iterative한 방식을 쓰는것 보다, substep으로 시간을 나눠서 반복하는게 더 높은 성능을 보였음.
  - physical and accurate
    - implicit Euler integration
    - newton minimization of a backward Euler integration step
    - non linear Gauss-Seidel method
    - 등의 이론적 기반.
    - 하지만 softness 처리에서 계수를 곱하는 방식은 unphysical하고, time-step 크기에 dependent하다는 문제가 생김. 
- XPBD
  - soft하지 않은 constraint처리에 대해서는 PBD와 동일하다. (stiffness가 inf)
  - constraint로부터 gradient를 계산하고, lambda를 계산할 때, time-step 크기에 dependent한 compliance alpha를 넣는다.
    - 이 compliance는 physical stiffness의 역수 개념이 된다.
  

이후 lecture에서는 변형가능한 dynamics를 구현하는 두가지 모델과 그 solver의 차이도 설명해주는데, 요약된 특성들을 나열한다.
- continuous model, global solver
- discrete model, local solver

### Interaction
lecture와 마찬가지로, 마우스 클릭과 drag-drop을 통한 간단한 interatction part를 작성했다. 이전 particle 예제에서 사용했던, ray-cast형식의 상호작용을 활용해서 클릭한 물체를 옮길 수 있도록 구현했다.  
아직 충돌에 관련된 내용을 구현하지 않아 물체들이 겹쳐진다.  

| | |
|:-:|:-:|
|![image](/images/vge-pbd/vge-pbd-23.png) | ![image](/images/vge-pbd/vge-pbd-24.png) |
|![image](/images/vge-pbd/vge-pbd-soft2d.gif) | ![image](/images/vge-pbd/vge-pbd-soft2d-3.gif)|

참고로, 출처한 자료에서는 three.js에 구현되어 있는 raycaster와 bounding sphere 기능을 사용하고 있다.

## Neighbor search

[](https://www.youtube.com/watch?v=D2M8jTtKi44)


충돌을 구현하기 위해 neighbor search를 통한 충돌 인식이 먼저 필요하다.

여기서는 lecture를 참고해서 spatial hashing 방식을 사용했다. 이 방식은 충돌 뿐 아니라, liquid, gas, sand, snow 등의 particle 기반 시뮬레이션에 모두 사용된다고 한다. 자세한 알고리즘은 영상에 설명되어 있어 요약해서 정리해놓으려 한다.

- neighbor search는 두 particle pi, pj의 거리가 d 이하인 i,j를 찾는 것이다. 이 거리 d가 2r이면, collision detection이 된다.
- naive한 방식. O(n^2)의 모든 particle pair에대해 intersection검사를 하는 방식.
- regular grid 방식.
  - particle의 center 좌표가 어떤 grid내부에 있는지를 저장하는 방식이다. 이 grid의 spacing 간격으로 좌표를 discretize하면 grid의 index를 얻을 수 있다.
  - 그 index 주변의 grid cell 들만을 대상으로 check하면 필요한 intersection check의 수를 크게 줄일 수 있다. (2D는 주변 9개, 3D는 27개의 grid cell)
  - 이 grid index를 사용하는 방식은 공간이 bounded여야만 가능하다. 그래서 필요한 개념이 hash table을 사용하는 것

### Spatial hash

hash table을 사용한 neighbor search 에서는 원하는 size의 table을 사용할 수 있다. 대신 서로 다른 두 grid cell이 하나의 table entry로 mapping되는 hash collision이 발생할 수 있으므로, hash function과 table size 등 설정에 주의해야한다.  

구현은 다음 자료들을 참고했다.
- [https://github.com/matthias-research/pages/blob/master/tenMinutePhysics/11-hashing.html](https://github.com/matthias-research/pages/blob/master/tenMinutePhysics/11-hashing.html)
- [https://carmencincotti.com/2022-10-31/spatial-hash-maps-part-one/](https://carmencincotti.com/2022-10-31/spatial-hash-maps-part-one/)
- hash table의 구현은 linked list로 구현하면 dense하지 않기때문에 별도의 array를 사용한 테크닉으로 구현하고 있다.
  - 기본적인 아이디어는, hash table에는 해당 hash key 값에 위치한 particle의 count만 저장하고, dense array에 순차적으로 그 particle의 index를 저장한다.
- 이를 구성하는 구조는 다음처럼 나눠진다.
  - 디테일은 영상 참고.
  - hash class
  - hash create
  - hash query
    - query를 했을 때, 주변 cell에 포함된 모든 particle indices를 반환한다.
    - hash collision에 의한 false positives는 단순하게 거리 check등으로 거를 수 있다.


### hash function

wip

## Collision by constraint

기존의 tetrahedron의 collision 처리는 다음 자료를 참고했다. (영상에서는 particle의 coliision을 다룬다.)

> [https://matthias-research.github.io/pages/publications/tetraederCollision.pdf](https://matthias-research.github.io/pages/publications/tetraederCollision.pdf)


- first pass
  - 모든 vertices를 cell에 classified되도록 계산한다. (spacing 크기로 나누는 작업)
  - 모든 tetrahedron의 bounding rectangle AABB를 계산해서 저장해둔다.
- second pass
  - 모든 tetrahedron에 대해서 cell에 classifed 되도록 한다.
  - 저장된 AABB를 통해 cell로 mapping하고, 그 cell에 해당하는 vertices(first pass에서 계산하둥)들 모두와 intersection test를 한다.
  - intersection test를 vertex가 tetrahedron을 관통하는지에 대해 검사하는데, barycentric coordinates를 사용.
    - 그 전에 AABB내부에 있는지 검사해서 먼저 필터링한다.
  - 이 방식을 사용하면, self-collision도 자연스럽게 처리가 가능하다.
    - vertex가 tetrahedron의 일부 그자체인 경우는 스킵
  
해당 자료에서는 time stamp를 사용해서 hash 초기화를 하지 않는 방식을 설명하는데, hash 생성에 관련된 부분은 영상의 방식을 선택했다.


먼저 좀 더 간단한 케이스인, edge-point의 collision을 distance constraint로 구현해서 동작을 확인했다.  
![image](/images/vge-pbd/vge-pbd-25.png)

[https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/issues/49](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics/issues/49)

collision handling의 경우는 rigid body의 velocity level에서 다뤄야하는데, 현재 예제들에서는 구현하지 않기로 했다.

collision detection과 handling에 있어서, 다른 구현들을 보면서 필요한 개념들을 찾게 되었다.
- distance field
- bounding volume hierarchy
- kd-tree
- contact point
등의 방식을 활용해서 system이 구축되어 있어야 일반적인 object간의 충돌 처리를 할 수 있을 것으로 파악했고, 우선은 constraint 기반 collision constraint 의 동작을 확인하는 것에 우선순위를 맞춰 간단한 구현을 진행했다.  
차선책으로 선택한 방식은, triangle과 point의 collision detection은 유지하고, handlind은 미리 저장해둔 surface(경계 edge들)와 particle을 통해 contact point를 계산해서 edge-point 의 signed distance constraint로 구현하는 방식이다.  
구현된 결과로 아래처럼, 충돌된 삼각형은 붉게 표시되고, 내부와 충돌하지 않도록 경계까지 밀어주는 constraint의 역할을 확인했다.  
![image](/images/vge-pbd/vge-pbd-26.png)

# 마무리

아직 남은 simulation 관련 내용이 많고, 복잡도도 올라간다. 다음은 GPU 기반의 simulation을 집중해볼 생각이다. 이번에도 collision detection 및 handling 기법들에 대해서는 깊이있게 직접 구현하지 않았는데, 이런 부분들은 구현 디테일을 혼자 만들어가기에는 지금 공부하고자 하는 GPU programming 및 graphics API 활용에서 너무 벗어나게 된다. (기하 알고리즘 공부하면서 병행실습해보면 재밌을 것 같다) 이론적으로 공부하고 넘어갈 부분과 좀 더 활용까지 구현해볼 부분을 잘 나눠서 계획해나가자.

어디서 주워들은 이야기들로 포스트를 마무리하려 한다.  
> 어떤 일을 시작할때, 어떻게 시작할지 감도 잡히지 않고 시작할 엄두가 안날때는 어떻게 해야할까?  
> 그냥 그 일을 하지 마라. 그 시작을 하지 못하는 것 자체가 진입장벽에 걸린 것이고, 그만큼 흥미가 없다는 뜻이다.  
> 진짜 하고 싶은 일은 어떻게든 찾아내서 뭔가를 시작하게 된다. 그게 1차 진입장벽을 넘은 것이다.

어느정도 공감이 됐다. 첫 직장을 퇴사하고 시간이 꽤 흘렀는데, 알고리즘 공부나 프로그래밍 기법등 공부도 잠시하고, kaggle 로 사이드 프로젝트도 해봤지만 하고 싶은 일을 한다기 보다는 이직을 준비하기 위해 해야되는 것들로 생각했던 것 같다. 거기서 한발짝 더 할 일들을 찾아나가지 못했다.   
graphics 관련 공부를 하고 Vulkan API 관련 tutorial와 예제 구현, 블로그 정리들을 하면서는 어떻게든 다음 step을 찾게 된다. 이 tutorial을 끝내면, 이 lecture를 끝내면, 이 예제구현을 끝내면 다음에 뭘 할지 어느샌가 다음에 하고 싶은 것을 리스트업해놓게 되고 느리더라도 그 다음 스텝으로 넘어갈 수 있게 됐다. 앞으로는 속도와 효율을 고려해서 스케쥴링하게되면 더 좋을 것 같다.

또 다른 얘기인데, 예전에 누가 청소하는 법을 알려준 적이 있는데 그게 생각이났다.  
> 매번 똑같은 청소를 하더라도 똑같은 부분만 하는게 아니라, 지난번 청소하지 않은 구석 창틀을 오늘 청소하고, 다음에는 또 어딘가 구석의 건들지 않은 부분을 청소해 나가야 한다는 말이었다. 큰 복도 가운데, 방 한가운데만 닦고 청소를 끝내면 매일 깨끗해진 것 같다고 착각하면서 구석에는 먼지가 더 쌓이게 될 수 있다는 것이다.

이번 내용을 정리하면서도 느꼈다. 몇번 본 키워드나 내용이라고 다 안다고 생각하고 넘어가거나, 더 자세히 다루기에는 무리라고 생각하고 넘어가면 평생 그 부분을 건들지 않을 것이다. 한번씩 마주쳤을 때, 조금이라도 새로운 내용이나 건들지 않았던 것들을 건드려주면 깨끗한 구역을 늘려갈 수 있지 않을까?  
그리고 나는 그 구석을 건드릴 수 있는 능력과 여건이 충분히 된다. 단지 핑계를 만들며, 익숙해진 편한 방식들을 추구하는 건 아닐지 경계심이 들었다.   
