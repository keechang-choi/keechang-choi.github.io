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
  - [renderLoop](#renderloop)
  - [triangle](#triangle)
  - [Interface](#interface)
    - [imGui](#imgui)
    - [CLI11](#cli11)
- [마무리](#마무리)
  - [readings](#readings)

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
  
# VGE - base
가정 먼저 여러 example 예제들의 공통 내용이 될 base를 작성하고, 첫 예제인 trinagle rendering을 작성하면서 정리한 내용이다.

[원본 base의 main부분](https://github.com/SaschaWillems/Vulkan/blob/master/base/vulkanexamplebase.h#L511-L521)  
를 참고하면 가장 먼저 main에서 실행되는 구조를 알 수 있는데,  
```c++
int main(const int argc, const char *argv[])													    
{																									
	for (size_t i = 0; i < argc; i++) { VulkanExample::args.push_back(arg[i]); };  				
	vulkanExample = new VulkanExample();															
	vulkanExample->initVulkan();																	
	vulkanExample->setupWindow();					 												
	vulkanExample->prepare();																		
	vulkanExample->renderLoop();																	
	delete(vulkanExample);																			
	return 0;																						
}
```


[구현한 base의 main부분](https://github.com/keechang-choi/Vulkan-Graphics-Example/blob/ui-overlay/src/base/vge_base.hpp#L134-L149) 나는 조금 다른 구조로 작성했다.

```c++
int main(int argc, char** argv) {            
    vge::VgeExample vgeExample{};           
    CLI::App app;                           
    vgeExample.setupCommandLineParser(app); 
    CLI11_PARSE(app, argc, argv);           
    vgeExample.initVulkan();                
    vgeExample.prepare();                   
    vgeExample.renderLoop();                
  } catch (const std::exception& e) {       
    std::cerr << e.what() << std::endl;     
    return EXIT_FAILURE;                    
  }                                         
  return 0;   
```

- 이 main은 macro로 선언되어있는데, examples에서 각자 호출해서 서로 독립된 실행파일을 만드는데 사용된다. 
  - example class가 base를 상속하기 때문에, 더 나은 구조로 작성할 수 있을 것 같은데 우선은 동일한 구조로 갔다.
- `setupWindow()` method 대신, window class의 unique_ptr을 통한 instance 생성으로 window 관련 처리를 했다. 원본 구조에서는 여러 OS를 지원하기때문에 window 설정이 모두 달라서 저런식으로 macro 사용을 통한 복잡한 구조가 되어 있는데, 나는 glfw를 사용한 windows OS에서의 window 생성만 구현했으므로 좀 더 간단하게 구조를 가져갔다.
- `initVulkan()` 에서는 기본적으로 Vulkan 사용을 위한, Vulkan instance나 physical device 관련 설정을 관리한다.
- `prepare()` 에서는 사용할 자원들에 대한 생성 및 초기화를 수행한다. 
- `renderLoop()` 에서는 실제로 rendering loop를 구현하고, 이벤트 처리나 FPS 측정 등 로직이 구성된다. 



## initVulkan

window 생성에 대한 내용이 추가된 것을 제외하면 대부분 원본과 동일하다. 전체적으로 vulkan-hpp wrapper를 쓸 것이므로 다음을 참고해서 작성했다.  
RAII 관련 기능들을 사용했는데, (원본과 비교했을 때, 메모리 해제 관련된 코드들을 신경 쓰지 않아도 돼서 훨씬 수월했다.) 사실 window 생성등이나 여러 자원 생성 부분에서 lazy loading과 관련된 목적에도 많이 사용을 해서 RAII라는 이름과 좀 뜻이 맞지 않는 부분도 있는 것 같긴 했다. vulkan-hpp의 raii wrapper에서도 이런식의 초기 값은 nullptr로 줘서 아예 생성을 하지 않고 lazy loading에 쓰는 부분이 많이 있다.  

- [Vulkan-Hpp/RAII_Samples/utils/utils.hpp at main · KhronosGroup/Vulkan-Hpp · GitHub](https://github.com/KhronosGroup/Vulkan-Hpp/blob/main/RAII_Samples/utils/utils.hpp)
- [Vulkan-Hpp/samples/utils/utils.hpp at main · KhronosGroup/Vulkan-Hpp · GitHub](https://github.com/KhronosGroup/Vulkan-Hpp/blob/main/samples/utils/utils.hpp)
- [Vulkan-Hpp/samples/utils/utils.cpp at main · KhronosGroup/Vulkan-Hpp · GitHub](https://github.com/KhronosGroup/Vulkan-Hpp/blob/main/samples/utils/utils.cpp)

이 함수는 virtual 로 선언돼서, base 하위의 example class의 `initVulkan()` 내부에서 호출된다. base에 포함된 내용들은 다음과 같다.
- VkInstance 생성
- debug messenger 설정
- physical device 생성
- queue family properties 설정
- logical device 생성
- queue 생성
- commandPool 생성
- depth format 설정
- window surface 생성
- VMA allocator 생성
  -  VMA를 써서 buffer와 image 생성 wrapper를 생성했는데, 관련 정보는 다음에서 얻을 수 있다.  
    [https://gpuopen-librariesandsdks.github.io/VulkanMemoryAllocator/html/usage_patterns.html](https://gpuopen-librariesandsdks.github.io/VulkanMemoryAllocator/html/usage_patterns.html)
  - 구현한 내용은 따로 [vgeu_buffer.cpp](https://github.com/keechang-choi/Vulkan-Graphics-Example/blob/main/src/base/vgeu_buffer.cpp)에 들어있다.

또한 이 함수 내부에서 사용하는 여러 기능들은 util로 빼서 따로 구현했다.  
[vgeu_utils.cpp](https://github.com/keechang-choi/Vulkan-Graphics-Example/blob/main/src/base/vgeu_utils.cpp)


## prepare
이 함수역시 virtual 로 선언돼서, base 하위의 example class의 `prepare()` 내부에서 호출된다. base에 포함된 내용은 다음과 같다.  
- swapChain 생성
- frameBuffer 와 관련 자원 생성
- renderPass 생성
- commandPool 생성
- draw command buffer 생성
- draw semaphores와 fences 생성
- ui overlay 생성



## renderLoop

- camera transform에 대한 및 update
- render loop
  - window의 종료 버튼에 대한 처리
  - `glfwPollEvents()`
  - view change update
  - Mouse input 처리
  - ui overlay update
  - `render()` 함수 호출
    - pure virtual로 선언된 이함수는 하위 class인 example에서 각각 구현된다.
  - FPS 측정 및 update에 사용될 timer count
- render loop 종료시 device wait idle 호출

## triangle

기존의 example repo 원본에서도, triangle 예시는 제일 처음으로 나온다. 차이점은, 원본에서는 첫 예제인 만큼 구현된 wrapper 들을 쓰지 않고 모든 코드를 triangle 예제에 설명과 함께 넣어놨지만, 나는 이미 구현해본 내용인 만큼 최대한 구현된 wrapper들을 활용하는 방식으로 작성했다.  
또 원본의 모든 예제에 해당되는 내용인데, single buffering만을 사용한 구현이 되어있어서 한번 queue에 제출한 내용은 모두 wait idle을 통해 기다리는 간단한 구조이다. 나는 double buffering 지원을 계속 할 수 있는 방식으로 구현하려고 하고, 이와 관련한 synchronization primitives 사용등의 부분에서 조금 변경을 했다. 
- 기본적으로 이 [issue](https://github.com/SaschaWillems/Vulkan/issues/871)에서 밝혀져는 것과 같이 이 원본 example repo는 기능 구현에 초점을 맞춰서 성능이나 synchronization 관련 최적화는 이뤄져있지 않다.
- 대부분 확인한 예제들에서 한 frame이 끝날때마다(command를 제출한 직 후) 바로 waitIdle을 통해서 queue에 제출된 command 들이 모두 실행을 완료할 때 까지 기다린다. 따라서 race condition이 발생할 경우를 줄인 간단한 구현들이 가능하다.
- 그래서 이전 tutorial에서와 마찬가지로, swapchain 이미지 수와 `MAX_FRAMES_IN_FLIGHT`(`MAX_CONCURRENT_FRAMES`) 값을 분리된 것으로 설정하고, 관련된 자원들도 `MAX_FRAMES_IN_FLIGHT` 값에 따라 복수개로 생성했다.

구현하면서 camera의 view matrix와 projection maxtrix 계산을 직접 하던 것에서, glm을 사용하는 방식으로 변경했다.  
처음에는 `glm::lookAt()`, `glm::perspective()`을 바로 호출해서 사용했는데, 의도와 다른 방향의 결과가 나왔다. 관련해서 내부 구현을 살펴보면서 left/right-handed system과 NDC 개념 등 헷갈렸던 것 들을 정리했다.

|             correct              |              wrong               |
| :------------------------------: | :------------------------------: |
| ![image](/images/vge-base-2.png) | ![image](/images/vge-base-3.png) |
| ![image](/images/vge-base-4.png) | ![image](/images/vge-base-5.png) |

- 자료 출처
  - [http://www.songho.ca/opengl/gl_projectionmatrix.html](http://www.songho.ca/opengl/gl_projectionmatrix.html)
  - [http://anki3d.org/vulkan-coordinate-system/](http://anki3d.org/vulkan-coordinate-system/)
  - [Vulkan default coord system for vertex positions - Stack Overflow](https://stackoverflow.com/questions/68508935/vulkan-default-coord-system-for-vertex-positions)
  - [https://stackoverflow.com/questions/21841598/when-does-the-transition-from-clip-space-to-screen-coordinates-happen](https://stackoverflow.com/questions/21841598/when-does-the-transition-from-clip-space-to-screen-coordinates-happen)
  - [https://learnopengl.com/Getting-started/Coordinate-Systems](https://learnopengl.com/Getting-started/Coordinate-Systems)
- 내용
  - 결과적으로 호출한 함수들은 `glm::lookAtLH()`, `glm::perspectiveLH_ZO()` 이다.
    - left-handed와 depth zero-to-one 에 해당하는 함수들이다.
  - 흔히 Vulkan에서는 right-handed coordinates, OpenGL에서는 left-handed coordinates라고 하는데 이게 정확이 어떤 개념일까?
    - 이 left or right의 기준은 NDC(Normalized Device Coordinate) 인데, NDC space는 다음과 같은 space transformation의 단계에서 나타나는 좌표계다.
      - local(or objects) space -> model matrix
      - world space -> view matrix
      - view(or eye, camera) spcae -> projection matrix
      - clip space -> perspective division
      - NDC space -> viewport transform
        - rasterization stage에서 일어나고, 이 normalized  된 좌표계를 벗어난 값들은 screen에 들어가지 않게 되면서 clipping이 일어난다.
      - screen space
    - 결론적으로, 이 left or right 의 개념은 API의 내부 NDC 기준이기때문에, 내가 view matrix와 projection matrix를 설정할때 필요한 world coordinate은 내 맘대로 정할 수 있고, 그에 맞는 변환을 지정해주면 되는 것이다.
  - glm 함수들의 이름이 Left/Right Handed인 이유는, 조금 misleading 할 수 있는데, +x와 +y 방향이 right, up인 기준에서 +z 방향이 forward인지, backward인지에 따라서 함수명을 정해서 라고 한다. 그래서 계산 상 실질적인 효과는 +z가 forward인지 backward인지로 matrix가 달라지는데 이때문에 우리는 +z가 forward 이기 때문에, left handed 함수를 쓰면 된다.


## Interface
[https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/1](https://github.com/keechang-choi/Vulkan-Graphics-Example/pull/1)  
화면에 text를 표시하거나, user interface를 위해서 Dear ImGuI라는 library를 사용했다. 여러 Graphics API와의 사용을 지원하고 간단하게 쓸 수 있는 장점이 있어보였다.
command line argument 는 따로 직접 구현하지 않고, CLI11 이라는 library를 추가했다.

### imGui
ImGui는 `bloat-free graphical user interface library for C++` 이라고 소개하는데, 

imGui vulkan example 을 참고해서 사용했다.
> [https://github.com/ocornut/imgui/blob/master/examples/example_glfw_vulkan/main.cpp](https://github.com/ocornut/imgui/blob/master/examples/example_glfw_vulkan/main.cpp)  


imGUI 사용은 다음 guide를 참고했다.  
> [https://vkguide.dev/docs/extra-chapter/implementing_imgui/](https://vkguide.dev/docs/extra-chapter/implementing_imgui/)

원본에서는 imgui에서 제공되는 backends기능들을 직접 구현해서 쓰는데(cross-platform 환경을 위해서로 보임), 나는 [imgui_impl_glfw backends](https://github.com/ocornut/imgui/blob/master/backends/imgui_impl_glfw.cpp) 의 기능들만 사용했다.  

![image](/images/vge-base-1.png)  
좌측 GUI에 띄워논 내용은 demo로 제공되는 내용인데, 모든 기능의 예시를 볼 수 있는 demo 여서 실행시켜보면서 필요한 기능들은 추후 추가하는 식으로 진행했다.  

### CLI11
[CLI11](https://github.com/CLIUtils/CLI11) 이라는 command line parser를 사용했다. 간단한 것들은 직접 문자열 처리를 해서 구현할 수 있을텐데 (실제로 원본의 방식), 최대한 기존 third-party들을 활용하기로 계획한 만큼, 이 library를 사용했다. 써보니 실제로 간단하고 직관적이어서 편했다.


CLI11 examples를 보고 사용예시에 맞는 내용들을 참고했다.
> [https://cliutils.github.io/CLI11/book/chapters/flags.html](https://cliutils.github.io/CLI11/book/chapters/flags.html)


![image](/images/vge-base-6.png)  
이미지 상단에 보면 다음 처럼 comand line argument를 주어 실행시켰는데, 앞으로의 예제들에서도 필요한 초기 옵션을 설정하는데 사용할 계획이다.

```
./traingle.exe -f 3 --height=720
```

ImGui를 활용한 옵션 선택과 겹칠수도 있는데, 엄격하게 구분하지 않고 필요시 자유롭게 두 기능을 모두 쓸 생각이다.

# 마무리

base 작성과 코드 structure 구현 등이 끝났으므로, 앞으로는 각 예제의 내용에 초점을 맞춰서 정리할 계획이다.  
렌더링 관련 코드를 작성할때 답답한 부분이, 초반에 아무것도 눈에 보이지 않을때인 것 같다. 뭔가 화면에 보이는게 달라진다면 변화를 주면서 디버깅 하거나 한 단계씩 추가하는게 용이할텐데, 아무것도 안나오는 검은 화면이 쭉 유지되다가 어느 순간 점프하면서 화면에 내용들이 보이기 시작한다. (디버깅 관련해서는 확실히 renderDoc 등의 툴 사용법을 익혀봐야겠다. 렌더링 관련 구현이 막혔을때 생산성이 달라지지 않을까?)  
Vulkan 공부법에 대한 자료([How to Learn Vulkan](https://www.jeremyong.com/c++/vulkan/graphics/rendering/2018/03/26/how-to-learn-vulkan/))에서도 나와있는 말인데, 
```
눈에 보이는 progress 가 없다고 해서 progress가 없다고 생각하지 마라
```
는 말이 떠올랐다.  
그래도 확실히 처음 Vulkan을 접했을 때 보다는 수월하고 빠르게 구현할 수 있기도해서, 어느정도 익숙해졌음을 느끼기도 했다.  
## readings
Vulkan API specification과 관련해서 잘 정리해놓은 블로그와 여러 설명 풍부한 블로그가 있어서 같이 남겨놓겠다. 

- [[ Vlukan 연구 ] 들어가며 :: 그냥 그런 블로그 (tistory.com)](https://lifeisforu.tistory.com/397)  
- [Vulkan의 파이프라인 베리어 : 네이버 블로그 (naver.com)](https://blog.naver.com/dmatrix/221858062590)

