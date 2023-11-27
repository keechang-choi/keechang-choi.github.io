---
title: "[WIP] Vulkan Graphics Examples - PBD"
date: 2023-11-24T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-pbd/vge-pbd-1.png
  thumbnail: /images/vge-pbd/vge-pbd-1.gif
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
### XPBD

![image](/images/vge-pbd/vge-pbd-18.png)
![image](/images/vge-pbd/vge-pbd-19.png)
![image](/images/vge-pbd/vge-pbd-20.png)
![image](/images/vge-pbd/vge-pbd-21.png)
![image](/images/vge-pbd/vge-pbd-22.png)
### Interaction

![image](/images/vge-pbd/vge-pbd-23.png)
![image](/images/vge-pbd/vge-pbd-24.png)
## Neighbor search
### Spatial hash
## Collision by constraint

![image](/images/vge-pbd/vge-pbd-25.png)
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
