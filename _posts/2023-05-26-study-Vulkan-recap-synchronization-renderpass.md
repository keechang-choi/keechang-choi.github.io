---
title: "Vulkan Tutorial - Recap Synchronization & RenderPass"
date: 2023-05-26T15:00:00
categories: 
  - study
tags: 
  - graphics

---

Vulkan Game Engine 영상에서 tutorial로 중간에 넘어오게 되면서, synchronization과 renderpass에서 가볍게 다루고 넘어간 내용들이 있어 구현에 헷갈리는 부분들이 있었다.  
특히 pipeline barrier와 subpass dependency 관련 내용 위주로 정리하고 현재 코드 구현에서 정확히 파악하고 있지 않은 부분들을 정리한 후, tutorial의 extra-chapter인 compute shader로 넘어가려 한다.

- [Synchronization](#synchronization)
  - [tutorial rendering and presentation](#tutorial-rendering-and-presentation)
    - [outline of a frame](#outline-of-a-frame)
    - [synchronization](#synchronization-1)
    - [semaphore](#semaphore)
    - [Fence](#fence)
    - [What to choose?](#what-to-choose)
    - [creating synchronization objects](#creating-synchronization-objects)
    - [이전 프레임 기다리기](#이전-프레임-기다리기)
    - [command buffer 녹화](#command-buffer-녹화)
    - [command buffer 제출](#command-buffer-제출)
    - [subpass dependency](#subpass-dependency)
    - [presentation](#presentation)
    - [Q. subpass dependency vs. semaphore](#q-subpass-dependency-vs-semaphore)
  - [CG at TU wien ep7](#cg-at-tu-wien-ep7)
    - [recap](#recap)
      - [commands](#commands)
      - [pipeline stages](#pipeline-stages)
      - [recording](#recording)
    - [wait idle operation](#wait-idle-operation)
    - [fences](#fences)
    - [semaphores](#semaphores)
    - [pipeline barriers](#pipeline-barriers)
    - [memory availability and visibility](#memory-availability-and-visibility)
    - [renderPass subpass dependencies](#renderpass-subpass-dependencies)
    - [events](#events)
  - [fix](#fix)
    - [frames in flight](#frames-in-flight)
    - [frame buffer and swapchain image](#frame-buffer-and-swapchain-image)
    - [single depth buffer](#single-depth-buffer)
    - [additional fence](#additional-fence)
- [RenderPass](#renderpass)
- [마무리](#마무리)


---


# Synchronization


## tutorial rendering and presentation
https://vulkan-tutorial.com/Drawing_a_triangle/Drawing/Rendering_and_presentation

먼저 tutorial의 위 챕터 내용을 정리해봤다.
### outline of a frame
tutorial에서는 다음과 같이 frame에 관련된 task들을 요약 가능하다.  
- 이전 frame이 끝나기까지 대기
- swapChain으로부터 image 얻기
- 이미지에 scene을 그리는 command buffer 녹화 (recording)
- 녹화된 command buffer 제출 (submit)
- swapChain image를 present

### synchronization
vulkan의 핵심 철학 중 하나가 gpu의 실행 동기화가 명시적이라는 것이다. synch primitives를 사용해서 연산의 순서를 정의하는데, vulkan api 호출들은 GPU에서의 작업이 비동기적으로 이뤄지고 그 작업 끝나기 전에 함수가 먼저 반환되기 때문이다.  
위의 작업들의 함수 호출은 실제로 끝나기 전에 반환되기 때문에 각 작업이 끝나고나서 실행되는 순서를 강제하기 위해서는 다음의 primitives를 잘 써야한다고 한다.

### semaphore
command buffer를 제출하는 등의 queue 연산의 순서를 주고 싶을때 쓴다.
- graphics queue
- presentation queue
두 가지가 현재 쓰였고, semaphore는 binary, timeline 두가지 종류가 있지만 우선 binary 타입만 다룬다.  

세마포어는 signaled or not 두 상태를 가지는데, 처음 시작은 unsignaled로 시작한다.  
같은 semaphore S를 한 queue operation에 signal sema로 지정하고, 다른 queue op에 wait sema로 지정하는 형식으로 사용된다.  

주의할 점으로, `vkQueueSubmit()` 호출은 바로 반환되고 실제 waiting은 GPU에서 발생한다는 것이다. CPU에서는 blocking 없이 계속 실행이 된다. CPU가 wait 하게 만드려면 다음의 Fence synch primitive를 사용해야 한다.

### Fence
host(CPU)에서 GPU의 연산이 언제 끝났는지 알 필요가 있을때 쓴다.  
fence도 signaled or not의 state를 가지는데, queue에 실행할 작업을 제출할때, 그 작업에 fence를 붙여 그 작업이 완료되면 fence가 signaled 되고 이후 host에서 특정 fence를 wait하는 방식으로 동작한다.

예시로, GPU에서 작업이 끝난 이미지를 CPU로 transfer한 후, file로 저장하고 싶을때 쓸 수 있다.

host를 block한다는 점이 semaphore와 차이점.

요약하면 semaphore는 GPU에서의 연산 실행 순서를 명시하고, fence는 CPU와 GPU가 서로 동기화 되도록 할 때 사용한다.


### What to choose?
현재 tutorial 구현에서 적용되어야할 부분이 두 군데가 있다.
- swapchain operations
- 이전 frame이 끝나기 기다리기.

swapchain 관련 연산들은 GPU에서 일어나기때문에 semaphore를 쓰면 된다.  

현재 구조에서는 매 frame 마다 command buffer를 re-recording 하고 있는데, *(미리 recording 해놓은 command buffer를 재사용 하는 방식도 가능하지만) 여기서는 recording을 Host에서 할 때, GPU에서 아직 실행되고 있는 command buffer에 overwrite하고 싶지 않기에 fence를 쓴다.

### creating synchronization objects
- 이미지를 swapcahin으로부터 얻어지고 렌더링 준비가 완료되었다는 signal을 위한 semaphore 
- 렌더링이 완료되어서 presentation이 가능하다는 semaphore
- 그리고 동시에 하나의 frame만 렌더링 되고 있도록 하는 fence

총 2개의 semaphore와 1개의 fence가 필요한데, 이전 LVE 구조에서는 fence를 한 종류 더 총 2개 종류를 쓰고 있었다. 이 부분에 대한 수정 history는 아래의 fix 에서 좀 더 자세히 다루려 한다.  
각 primitive들은 `MAX_FRAMES_IN_FLIGHT` 별로 하나씩 필요하다.  

### 이전 프레임 기다리기
처음 `acquireNextImate()` 에서 이 fence를 기다린 후 `vkAcquireNextImageKHR()` 를 호출한다. 이때 초기 설정은 signaled 되어 있도록 한다.
`imageAvailableSemaphore` 는 이미지를 얻어오는 작업이 끝나면 signaled 되도록 인자로 지정해준다.

### command buffer 녹화
`vkResetCommandBuffer()` 관련해서 차이점이 있는데, 이는 tutorial 구현과 다르게, command pool 생성시 `VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT` 사용 여부와 관련이 있다.  
https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/VkCommandPoolCreateFlagBits.html

### command buffer 제출
submitInfo 관련
- 어떤 semaphore를 사용해서 wait할지
  - `imageAvailableSemaphore` 
  - draw등 제출한 command들은 그 swapchain에서 이미지를 얻어오는 것이 완료된 이후에 그 이미지에 write을 하고 싶다.
- 어떤 pipeline stage에서 기다릴지
  - `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT`
  - 최적화와 관련된 부분인데, graphics pipeline stages에서 이미지가 사용가능한 상태가 아니더라도, color attachment output stage 이전까지는 gpu에서 실행이 되도록 하고 싶다는 뜻이다.
- 이 제출한 command들이 완료되면 signal을 보낼 semaphore가 있는지?
  - `renderFinishedSemaphore` 
  - 이 semaphore를 사용해서 렌더링이 끝난 이미지를 present하도록 설정해준다.

### subpass dependency

renderPass에 있는 subpass에서는 이미지의 layout transition을 명시하지 않아도 고려한다. 
이 transition은 subpass들간의 memory & execution dependency를 명시한다.

기본 built-in dependencies는 render pass의 시작과 끝에서의 transition에 관한 것인데, 시작 부분에서는 이미지를 아직 얻어오지 않을 수 있는 문제가 있다. 
> `vkCmdBeginRenderPass()` 를 가장 먼저 recording 하는데, 그 시점에서 built-in dependency에 의한 image layout transition이 일어나기에는 문제가 있다는 뜻으로 이해함.   
두가지 해결법이 있는데,
- draw command 를 제출할 때, `imageAvailableSemaphore` 의 waitStages를 `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT`로 주어서, render pass가 이미지가 가용해진 이후에 시작하도록 하거나 (최적화 관련 단점이 될 듯?)
- subpass dependency를 명시해서 `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT` 로 지정하는 방법.
  - subpass dependency를 external -> 0 명시해서 직전 subpass 지정
  - srcStageMask를 `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT`로 지정, dstStageNask를 `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT`로 지정.
  - srcAccessMask를 0, dstAccessMask를 `VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT` 로 지정
  - 직전 subpass의 color output stage와 현재 subpass의 color output stage 사이에서 any -> color write 로의 layout transition이 이뤄지도록 지정해줌.
  - 사실 이 부분 관련해서 여러 설명을 검색해봤는데, 잘 이해가 안됐다. 아래의 영상 관련 내용 정리에서 추가할텐데, spec 문서의 first, second synchronization scope를 그대로 이해하는게 가장 정확한 설명인 것 같아 정리해놓으려 한다.

### presentation

graphics queue submit이 끝난 후, `renderFinishedSemaphore` 를 wait로 주어서 `vkQueuePresentKHR()` 를 호출한다.  
graphics queue submit에서 signal sema로 지정해놓았기 때문에, rendering이 끝날때까지 기다렸다가 presentation engine으로 요청을 하게 한다.

---
### Q. subpass dependency vs. semaphore
> Q. subpass dependency와 semaphore의 설정이 각각 필요한 이유가 뭔지? 서로 중복되는 내용은 아닌지?  
> https://stackoverflow.com/questions/59693320/use-of-vksubpassdependency-vs-semaphore
> 
> A. semaphore에서 지정해주는 `pWaitDstStageMask`는 같이 제출한 command 실행하기 전까지 기다릴 어떤 pipeline stage를 명시하는 것이고, `vkAcquireNextImageKHR()` 에서 주는 image index는 queue 연산이 아니기 때문에 presentation engine에서 그 이미지의 사용이 끝났는지 알수가 없기 때문에 필요했던 것임.  
> 
> 반대로 subpass dependency는 layout transition이 언제 일어날지에 대한걸 지정해주기 때문에 필요함. 지정하지 않으면 아무때나 알아서 일어날텐데, presentation engine에서 아직 이미지를 읽고 있는데 layout을 바꾸버리는 상황이 발생 가능함. (지정하지 않은 `srcStageMask`는 `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT`가 default.)  
> 
> 이걸 막기위해, `pWaitDstStageMask`를 top of pipe (all commands) 로 주면, vertex processing등도 하지 않고 모든 것을 기다린 다음 시작하니까 layout 변경이 없어도 되긴함. 근데 optimal 하지 않을 수 있음.
> 
> 그래서 우리가 하려는 방식은 layout transition의 `srcStageMask`를 `VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT`로 지정해서 이 이후에 write로 변경을 하는 방식. 이전 render pass의 commands들이 이 color att output stage에 도달한 이후에 layout transition이 일어나도록 강제하는 것인데, 이 시점은 sema wait가 끝난 시점이므로, presentation engine이 그 이미지 사용을 끝냈고, image layout을 변경해도 괜찮게 됨. 
> 여기서 헷갈렸던 부분은, swap chain 이미지가 여러개 있는 상황에서는 이전 render pass에서 presentation engine이 image를 사용하고 있더라도 이번 render pass에서는 layout transition을 해도 문제가 없지 않냐는 의문이었는데, 이 swap chain 이미지의 수와는 독립적으로 (최악의 경우 1개인 상황에서도) 실행에 문제가 없도록 보장하기 위한 내용이라고 이해하고 넘어갔다.



이 시점에서 헷갈렸던 것이, 어떤 개념이 (commands, pipeline, render pass, subpass)이 실행 (execution)과 관련이 이떻게 있는지에 대한 큰 그림이었다. 

https://stackoverflow.com/questions/65047176/vulkan-is-the-rendering-pipeline-executed-once-per-subpass

해당 내용을 찾아보다가 언급된 아래의 CG at TU wien Series영상을 보고 이런 큰 흐름을 이해하는데 도움이 되었다.
## CG at TU wien ep7

https://www.youtube.com/playlist?list=PLmIqTlJ6KsE1Jx5HV4sd2jOe3V1KMHHgn

이 series 내용들을 통해 명확히 이해하지 않고 넘어갔던 개념들을 한 번 크게 볼 수 있었다. animation과 적절한 이미지가 곳곳에 등장해서 글로 정리할수 있는 부분은 많지 않은 것 같다. 마지막 내용인 synch 관련 내용만 정리해놓으려 한다.

### recap
#### commands
#### pipeline stages
#### recording
### wait idle operation
### fences
### semaphores
### pipeline barriers
### memory availability and visibility
### renderPass subpass dependencies
### events
## fix
기존 LVE 코드 구조와 vulkan-tutorial.com 에서의 코드 구조 차이가 있는 부분들이 있어서 여기서 수정하고 넘어갔다. 아마 기본 구조는 같은데, vulkan-tutorial.com의 repo history를 보니, 여러 PR들이 합쳐지면서 수정된 내용이 LVE 코드에 대응되는 비슷한 부분과 차이가 벌어졌던 것으로 보인다.

### frames in flight

### frame buffer and swapchain image

### single depth buffer

### additional fence

# RenderPass

# 마무리

