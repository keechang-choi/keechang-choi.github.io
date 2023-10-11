---
title: "[WIP] Vulkan Graphics Examples - Particles"
date: 2023-10-02T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-particle-42.png
  thumbnail: /images/vge-particle-42.png
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
    - [specialization Constants](#specialization-constants)
  - [two-body simulation and verification](#two-body-simulation-and-verification)
  - [trajectory](#trajectory)
    - [line drawing](#line-drawing)
  - [physics and numerical integration](#physics-and-numerical-integration)
    - [integration method 비교](#integration-method-비교)
- [mesh attraction](#mesh-attraction-1)
  - [interaction](#interaction)
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
  - 기본 틀은 위 예제를 따라가며 작성할 계획이다. 이전 보다 조금 더 복잡한 계산이 compute shader에서 실행되는 만큼, shared memory 사용 및 compute pipeline 구성과 syncrhonization에 초점을 맞췄다.
  - [Vulkan/examples/computenbody/computenbody.cpp at master · SaschaWillems/Vulkan (github.com)](https://github.com/SaschaWillems/Vulkan/blob/master/examples/computenbody/computenbody.cpp)
- 아래 자료들은 모두 particle dreams 예시의 내용을 다루는데, webGL로 작성된 것들은 demo를 브라우저에서 실행해볼 수 있게 되어 있어서 실행해보며 어떤 기능들을 넣을지 구상할 수 있었다.
  - [Particle Dreams (karlsims.com)](http://www.karlsims.com/particle-dreams.html)
  - [A Particle Dream | Nop Jiarathanakul (iamnop.com)](https://www.iamnop.com/works/a-particle-dream)
  - [https://github.com/byumjin/WebGL2-GPU-Particle](https://github.com/byumjin/WebGL2-GPU-Particle)
- animation in compute shader
  - 이전 예제에서 animation 계산을 (정확히는 animation update는 cpu에서 하고, 계산된 joint matrices를 활용한 skinning) vertex shader에서 실행했는데, 이번 예제 구현에서는 vertex shader 이전에 모든 animation이 완료된 animated vertices data가 SSBO형태로 필요하다. 
    - 이 animated vertices를 target으로 particle이 attraction 되는 효과를 만들 계획인데, 자세하게는 이 particle을 수치 적분하기 이전의 calculate compute shader에서 이 자료가 사용될 예정이다.
    - 이를 위해서 비슷한 자료를 찾아보던 중 다음의 rust로 작성된 vulkan viewer 예제에서 구조를 참고했다.
  - [rustracer/crates/examples/gltf_viewer/shaders/AnimationCompute.comp at main · KaminariOS/rustracer (github.com)](https://github.com/KaminariOS/rustracer/blob/main/crates/examples/gltf_viewer/shaders/AnimationCompute.comp)

# Prerequisites
## numerical integration
Euler method  
Runge-Kutta method  

## mesh attraction

# Plan

## 작업 순서
## CLI11 and ImGui

# Progress
## synchronization
## memory barrier

## particle rendering
![image](/images/vge-particle-0.png)  
![image](/images/vge-particle-1.png)  
![image](/images/vge-particle-2.png) 

## particle-calculate-integrate

### pipeline 구성
### specialization Constants

![image](/images/vge-particle-3.png)  
![image](/images/vge-particle-4.png)  
![image](/images/vge-particle-5.png)  


![image](/images/vge-particle-2.gif) 

![image](/images/vge-particle-6.png)  
![image](/images/vge-particle-7.png)  
![image](/images/vge-particle-8.png)  
![image](/images/vge-particle-9.png)  

## two-body simulation and verification

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