---
title: "Vulkan Graphics Examples - PBD"
date: 2023-11-24T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-pbd/vge-pbd-1.png
  thumbnail: /images/vge-pbd/vge-pbd-1.gif
---

Position Based Dynamics관련 내용들을 습득하고, 예제들을 구현해보기로 했다. 렉쳐에는 영상과 구현 자료가 잘 정리되어 있고, 논문 및 course 등 정확한 정보가 충분해서 공부하기 좋았다.  
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
# Integration Method
- Euler method
- implicit Euler method
  - (backward)
- Semi-implicit Euler method
  - Symplectic Euler method
- Mid-point method
- Verlet method

# Lectures & Plan

[Ten Minute Physics (matthias-research.github.io)](https://matthias-research.github.io/pages/tenMinutePhysics/index.html)

https://www.youtube.com/watch?v=oPuSvdBGrpE

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


![image](/images/vge-pbd/vge-pbd-2.png)
![image](/images/vge-pbd/vge-pbd-3.png)
![image](/images/vge-pbd/vge-pbd-4.png)

## 2D simulation setup
![image](/images/vge-pbd/vge-pbd-5.png)

## Cannon ball

![image](/images/vge-pbd/vge-pbd-6.png)

## Ball collision - naive
![image](/images/vge-pbd/vge-pbd-7.png)

## Beads on wire
![image](/images/vge-pbd/vge-pbd-8.png)

![image](/images/vge-pbd/vge-pbd-9.png)
### Constraint dynamics

![image](/images/vge-pbd/vge-pbd-17.png)

## Triple pendulum

![image](/images/vge-pbd/vge-pbd-10.png)
![image](/images/vge-pbd/vge-pbd-11.png)
![image](/images/vge-pbd/vge-pbd-12.png)


![image](/images/vge-pbd/vge-pbd-13.png)
![image](/images/vge-pbd/vge-pbd-14.png)
![image](/images/vge-pbd/vge-pbd-15.png)

![image](/images/vge-pbd/vge-pbd-16.png)

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
최근에 이런말들 들었다. 
> 어떤 일을 시작할때, 어떻게 시작할지 감도 잡히지 않고 시작할 엄두가 안날때는 어떻게 해야할까?  
> 그냥 그 일을 하지 마라. 그 시작을 하지 못하는 것 자체가 진입장벽에 걸린 것이고, 그만큼 흥미가 없다는 뜻이다.  
> 진짜 하고 싶은 일은 어떻게든 찾아내서 뭔가를 시작하게 된다. 그게 1차 진입장벽을 넘은 것이다.

어느정도 공감이 됐다.



