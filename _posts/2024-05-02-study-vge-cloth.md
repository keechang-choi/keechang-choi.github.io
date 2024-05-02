---
title: "[WIP] Vulkan Graphics Examples - Cloth"
date: 2024-05-02T15:00:00
categories: 
  - study
tags: 
  - graphics
image: 
  path: /images/vge-cloth/vge-cloth-26.png
  thumbnail: /images/vge-cloth/ex-cloth-8.gif
---

- [Theoretical Background](#theoretical-background)
  - [Existing example implementation](#existing-example-implementation)
  - [PBD lecture summary](#pbd-lecture-summary)
    - [Lec 14](#lec-14)
    - [Lec 15](#lec-15)
    - [Lec 16](#lec-16)
- [Implementation](#implementation)
  - [Plans](#plans)
  - [SSBO draw](#ssbo-draw)
  - [Constraint compute](#constraint-compute)
  - [Triangle mesh \& Normal vector](#triangle-mesh--normal-vector)
    - [stretch constraint demo](#stretch-constraint-demo)
    - [Atomic operations](#atomic-operations)
  - [Mouse Ray casting interaction](#mouse-ray-casting-interaction)
  - [Geometry shader](#geometry-shader)
  - [Results \& Further study](#results--further-study)
    - [Demo](#demo)
    - [TODOs \& Not TODOs](#todos--not-todos)
- [마무리](#마무리)


# Theoretical Background

cloth simulation on GPU
compute shader

## Existing example implementation

[Vulkan/examples/computecloth/computecloth.cpp at master · SaschaWillems/Vulkan (github.com)](https://github.com/SaschaWillems/Vulkan/blob/master/examples/computecloth/computecloth.cpp)

[Vulkan/shaders/glsl/computecloth/cloth.comp at master · SaschaWillems/Vulkan (github.com)](https://github.com/SaschaWillems/Vulkan/blob/master/shaders/glsl/computecloth/cloth.comp)

## PBD lecture summary

[Ten Minute Physics](https://matthias-research.github.io/pages/tenMinutePhysics/index.html)

### Lec 14

![](https://www.youtube.com/watch?v=z5oWopN39OU)

### Lec 15

![](https://www.youtube.com/watch?v=XY3dLpgOk4Q)

### Lec 16

![](https://www.youtube.com/watch?v=q4rNoupGr8U)


# Implementation
## Plans
## SSBO draw

![image](/images/vge-cloth/vge-cloth-1.png)

![image](/images/vge-cloth/vge-cloth-2-2.png)

![image](/images/vge-cloth/vge-cloth-2-1.png)

![image](/images/vge-cloth/vge-cloth-0.png)

## Constraint compute

![image](/images/vge-cloth/vge-cloth-2.png)

![image](/images/vge-cloth/vge-cloth-3.png)

![image](/images/vge-cloth/vge-cloth-4.png)

![image](/images/vge-cloth/vge-cloth-5.png)

![image](/images/vge-cloth/vge-cloth-6.png)

![image](/images/vge-cloth/vge-cloth-7.png)

## Triangle mesh & Normal vector

![image](/images/vge-cloth/vge-cloth-8.png)

![image](/images/vge-cloth/vge-cloth-9.png)

![image](/images/vge-cloth/vge-cloth-10.png)

![image](/images/vge-cloth/vge-cloth-11.png)

![image](/images/vge-cloth/vge-cloth-12.png)

![image](/images/vge-cloth/vge-cloth-13.png)

![image](/images/vge-cloth/vge-cloth-14.png)

### stretch constraint demo

![image](/images/vge-cloth/ex-cloth-7-stretch.gif)

### Atomic operations

![image](/images/vge-cloth/vge-cloth-15.png)

![image](/images/vge-cloth/vge-cloth-16.png)

![image](/images/vge-cloth/vge-cloth-17.png)

## Mouse Ray casting interaction

![image](/images/vge-cloth/vge-cloth-18.png)

![image](/images/vge-cloth/vge-cloth-19.png)

## Geometry shader

![image](/images/vge-cloth/vge-cloth-20.png)

![image](/images/vge-cloth/vge-cloth-21.png)

![image](/images/vge-cloth/vge-cloth-22.png)

![image](/images/vge-cloth/vge-cloth-23.png)

## Results & Further study

![image](/images/vge-cloth/vge-cloth-24.png)

![image](/images/vge-cloth/vge-cloth-25.png)

![image](/images/vge-cloth/vge-cloth-26.png)

### Demo

options
![image](/images/vge-cloth/ex-cloth-1-low.gif)

wireframe and backface
![image](/images/vge-cloth/ex-cloth-2-low.gif)

mouse drag interaction
![image](/images/vge-cloth/ex-cloth-3-low.gif)

geometry shader for normal debugging
![image](/images/vge-cloth/ex-cloth-4-low.gif)

single animating model collision
![image](/images/vge-cloth/ex-cloth-5-low.gif)

two animating model collision
![image](/images/vge-cloth/ex-cloth-6-low.gif)

stationary model and animating model collision
![image](/images/vge-cloth/ex-cloth-8.gif)

### TODOs & Not TODOs

- self-collision
- optimize
- multiple cloth simulation
- improve model collision 

  

# 마무리

deferred rendering

depth-stencil

multi-thread command buffer
