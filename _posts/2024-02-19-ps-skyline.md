---
title: "Problem Solving: skyline"
date: 2024-02-19T15:00:00
categories: 
  - study
tags: 
  - ps
  - computational geometry
image: 
  path: /images/ps-skyline/ps-skyline1.png
  thumbnail: /images/ps-skyline/ps-skyline1.png
---

이전에 직장에서 computational geometry study를 가진적이 있다.  
그때 알게된 문제인데 skyline problem이라고 하는 유명한 문제가 leetcode에도 있어서 이 문제를 풀고 개선하려고 정리했던 적이 있다.  
정리해두고 잊고 있었는데, 블로그에 올려두려 한다.

- [문제 설명](#문제-설명)
- [기존 해법](#기존-해법)
- [개선 알고리즘](#개선-알고리즘)
- [아이디어](#아이디어)
- [구현](#구현)
- [검증 및 시각화](#검증-및-시각화)
- [코드 자료](#코드-자료)
- [10^4](#104)


---

# 문제 설명

> [https://leetcode.com/problems/the-skyline-problem/](https://leetcode.com/problems/the-skyline-problem/) 

먼저 skyline problem 문제 정의는 위 leetcode에서 명확히 알 수 있다. 간단하게는 빌딩이 여러개 겹쳐있을때, 하늘의 선이 어떻게 될지 찾으라는 문제인데 시간 복잡도를 줄이는게 핵심인 문제다.

# 기존 해법

보통 PS 에서 요구되는 입력 범위와 알고리즘은 O(n log n)을 요구한다.  
대부분의 해법을 찾아보면 priority queue를 활용한 방법이나, divide and merge 로 풀 수 있다. 

- segments에는 건물의 x 값과 건물 index를 pair로 넣고 정렬한다. (시작점과 끝점의 x 모두)  
- priority queue에 높이와 건물이 끝나는 x 좌표를 같이 저장한다. (이때  우선순위는 높이, x좌표 큰 순)
- x 순으로 segment를 도는 loop.  
  - 현재 seg에 저장된 x 값이 현재 event x와 같을 동안 다음 seg로 반복한다. (같은 x 좌표에 여러 building이 겹칠때)
    - 현재 seg에 저장된 건물의 시작 x값이 현재 event x와 같으면 높이와 끝 x 값을 pq에 추가한다.
  - pq에 들어있는 top부터 이미 event x 가 건물의 끝점을 지나간 것들은 pq에서 pop
  - pq의 top에서 현재 높이를 얻는다. (이때 pq가 비어있으면 0이 되도록 설정)
  - 이 높이가 이미 skyline의 마지막 값과 다른 경우만 event x 와 그 높이를 추가해준다. (같으면 이어져야함)



```c++
  // find skyline given building segments in O(n log n)
  std::vector<std::vector<int>> GetSkylineSlow(
      std::vector<std::vector<int>>& buildings) {
    std::vector<std::vector<int>> skyline;

    std::vector<std::pair<int, int>> segs;
    segs.reserve(buildings.size());
    for (int i = 0; i < buildings.size(); i++) {
      const auto& b = buildings[i];
      segs.push_back({b[0], i});
      segs.push_back({b[1], i});
    }

    std::sort(segs.begin(), segs.end());

    std::priority_queue<std::pair<int, int>> pq;

    int seg_idx = 0;
    while (seg_idx < segs.size()) {
      int cur_x;
      std::tie(cur_x, std::ignore) = segs[seg_idx];
      while (seg_idx < segs.size() && cur_x == segs[seg_idx].first) {
        int building_idx;
        std::tie(std::ignore, building_idx) = segs[seg_idx];
        const auto& b = buildings[building_idx];
        if (b[0] == cur_x) {
          pq.push({b[2], b[1]});
        }
        seg_idx++;
      }

      // remove immediately as it ends
      while (!pq.empty() && pq.top().second <= cur_x) {
        pq.pop();
      }
      int cur_height = 0;
      if (!pq.empty()) {
        cur_height = pq.top().first;
      }

      if (skyline.empty() || skyline.back()[1] != cur_height) {
        skyline.push_back({cur_x, cur_height});
      }
    }

    return skyline;
  }

```


다음은 고려할 corner case등을 생각한 과정이다.  

![image](/images/ps-skyline/ps-skyline2.png) 


# 개선 알고리즘

이 문제를 시간복잡도 O(n log h)에 풀수 있다는 정보를 study중 알게되었는데, 이때 h는 output으로 나오는 skyline의 point 수이다. 이런 알고리즘을 [output-sensitive](https://en.wikipedia.org/wiki/Output-sensitive_algorithm) 알고리즘 이라고 하는데, 계산기하학 분야에서 자주 나온다.  
output의 수가 적게 예상되는 상황에서 효율적인 방식인데, skyline problem도 빌딩의 수 n이 매우 커지면 겹치는 부분들로 인해 최종 skyline의 수는 적을것으로 예상할만한 상황이다.  


# 아이디어

이 output-sensitive한 알고리즘의 대표적인 방식으로 convex hull 을 찾는 [Chan's algorithm](https://en.wikipedia.org/wiki/Chan%27s_algorithm) 이 있는데, 이와 유사한 아이디어로 문제를 접근하기로 했다.

- 최종 skyline의 수를 h라고 하고, 이 값은 알 수 없으므로 먼저 h*라고 guess한다.
- 그다음 각 building을 h*개씩 묶어서 k개의 그룹을 만든다.
- 각 그룹에서 skyline을 찾는다. (이전의 우선순위 큐 방식 사용)
  - O(k x (h* log h*)) = O(n log h*)
- 각 그룹에서 ray query를 할 수 있는 구조를 구축한다.
  - O(k x (h* log h*))
- 각 그룹의 skyline을 하나로 합친다.
  - 시작점에서 모든 k개의 그룹으로 query를 날려서 가장 가까운 segment로 이동한다.
    - O(k x log h*)
  - 이 query 후 이동 과정을 한번 하면 최종 skyline의 점 하나를 얻으므로,  h 번 반복하면 정답을 얻어야 한다. guess했던 h*가 h 보다 크거나 같다면 어쨌든 정답을 찾을 수 있다.
    - O(n log h*)
- 이제 이 h*를 작은 값에서부터 늘리면서 정답을 찾을 수 있을때까지 늘리면 된다.
  - 이 늘리는 방식은 2^(2^i) 형태로 늘리는데, 이렇게 늘려야 모든 합을 계산했을 때, O(n log h)를 달성할 수 있다.


![image](/images/ps-skyline/ps-skyline3.png) 

이 query는 다음과 같이 한 점에서 수평선으로 ray를 쐈을 때, 어떤 vertical segment와 먼저 만나는지 반환해야하는데, O(log n)의 시간복잡도를 보장해야하고, 구축할때 O(n log n)의 시간복잡도를 만족해야 한다.  


range tree나, kd tree 등 여러 tree 구조의 데이터를 구축해야 탐색 시 시간복잡도를 만족할 것으로 생각하고 조사해봤다.  
결국 선택한 방식은 y좌표로 한번, x좌표로 한번 두개의 binary search를 하도록 구성하는 방식인데, 이를 구성할 때 시간을 줄이기 위해 [fractional cascading](https://en.wikipedia.org/wiki/Fractional_cascading) 기법을 사용했다.  

query 과정을 나타낸 모식도이며 세부 알고리즘은 구현 코드와 주석으로 대체하려한다.
![image](/images/ps-skyline/ps-skyline4.png) 

# 구현


![image](/images/ps-skyline/ps-skyline5.png) 

초기 구현 결과로 복잡한 예시를 넣어봤다. 오류가 몇가지 있었는데 수정한 내용이다.
- next sub group point exist 중 drop 조건
- 그후 prev로 drop하기 전에, current next y로 self drop이 더 높으면 drop하지 않도록 조건을 변경
  
해당 이슈를 수정한 후 원하는 결과를 얻었다.  
![image](/images/ps-skyline/ps-skyline6.png) 

보기 편하게 20개 건물로 확인한 결과이다.  

![image](/images/ps-skyline/ps-skyline9.png) 

구현과정에서는 테스트 케이스를 하나씩 추가해가며 각 기능의 구현완료를 확인하고 넘어갔다.  

# 검증 및 시각화

가장 먼저 시각화 코드를 작성해서 눈으로 결과의 오류를 확인하고 수정할 부분을 건드렸다.  
그 이후 각 부분별로 실행시간을 확인했다.  
![image](/images/ps-skyline/ps-skyline8.png) 


- preprocess는 O(n)이 예상되는 부분인데 조금 오래걸린것으로 보고, copy 최적화로 절반 가량 줄였다.
- subgp skyline 시간 총합
- 각 query tree 구축 시간
  - 이부분이 가장 시간을 많이 쓰고 있어서 최적화의 여지가 있지만 남겨두었다.
- h* loop의 각각 query 시간


![image](/images/ps-skyline/ps-skyline7.png) 

이후에는 n을 키워가며 기존의 알고리즘과 제안한 알고리즘의 시간이 얼마나 걸리는지 측정했다.  
n의 범위가 작을때는 priority queue 방식이 더 빨랐지만, n이 10^6을 넘어가면서부터는 개선된 시간을 보였다. 이 n은 최적화를 통해 더 줄일 수 있을 것으로 판단했다.  
하지만 이런 asymptotic analysis 자체가 practical 한 측면 보다는 theoretical한 분석위주이기 때문에, 실제 알고리즘에는 불필요한 constant term을 줄일필요가 있을 것이다. 참고로 leetcode에서 제공되는 n의 최대값은 10^4으로 기존 알고리즘이 더 나은 성능을 보이는데, 여러 이론상 빠른 알고리즘들도 구현상 복작도나, n이 작은 경우 느려서 쓰이지 않는 케이스가 많이 있기때문에 큰 문제는 아니라고 생각했다.

# 코드 자료


<details>
<summary>전체 알고리즘과 테스트 코드, 프로파일링 코드</summary>
{% highlight c++ %}
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <queue>
#include <random>
#include <sstream>
#include <tuple>
#include <unordered_map>
#include <vector>

class Node {
 public:
  Node* left;
  Node* right;
  int y_med;
  std::vector<int> x_sorted_idx;
  std::vector<int> left_x_cascading_map;
  std::vector<int> right_x_cascading_map;
  std::vector<int> left_x_cascading_map_inverse;
  std::vector<int> right_x_cascading_map_inverse;

  Node(int y_med_, const std::vector<int>& x_sorted_idx_)
      : y_med(y_med_), x_sorted_idx(x_sorted_idx_) {
    left = nullptr;
    right = nullptr;
  }
};

class Tree {
 public:
  Node* root;
  const std::vector<std::vector<int>>& pts;
  std::vector<int> x_sorted_idx;
  std::vector<int> y_sorted_idx;
  std::vector<int> idx_to_y_order;
  int td1, td2, td3, td4, td5, td6;
  Tree(const std::vector<std::vector<int>>& pts_) : pts(pts_) {
    // TODO: remove O(n) copys using only sort.
    std::chrono::high_resolution_clock::time_point begin;
    std::chrono::high_resolution_clock::time_point end;
    std::chrono::high_resolution_clock::time_point tp0;
    std::chrono::high_resolution_clock::time_point tp1;
    std::chrono::high_resolution_clock::time_point tp2;
    int time_diff;

    begin = std::chrono::high_resolution_clock::now();

    // std::vector<std::tuple<int, int, int>> indexed_xy;
    // indexed_xy.reserve(pts_.size());
    // for (int i = 0; i < pts.size(); i++) {
    //   indexed_xy.emplace_back(i, pts[i][0], pts[i][1]);
    // }

    // std::sort(indexed_xy.begin(), indexed_xy.end(),
    //           [](const auto& a, const auto& b) {
    //             int a_x;
    //             std::tie(std::ignore, a_x, std::ignore) = a;
    //             int b_x;
    //             std::tie(std::ignore, b_x, std::ignore) = b;
    //             return a_x < b_x;
    //           });
    // x_sorted_idx.reserve(pts_.size());
    // for (const auto& item : indexed_xy) {
    //   int idx;
    //   std::tie(idx, std::ignore, std::ignore) = item;
    //   x_sorted_idx.push_back(idx);
    // }
    x_sorted_idx.reserve(pts_.size());
    // y_sorted_idx.reserve(pts_.size());
    for (int i = 0; i < pts_.size(); i++) {
      x_sorted_idx.push_back(i);
      // y_sorted_idx.push_back(i);
    }

    // x_sorted_idx.resize(pts_.size());
    // std::iota(x_sorted_idx.begin(), x_sorted_idx.end(), 0);
    tp0 = std::chrono::high_resolution_clock::now();
    y_sorted_idx.reserve(pts_.size());
    for (int i = 0; i < pts_.size(); i++) {
      y_sorted_idx.push_back(i);
    }
    tp1 = std::chrono::high_resolution_clock::now();

    std::stable_sort(
        y_sorted_idx.begin(), y_sorted_idx.end(),
        [&pts_](int i1, int i2) { return pts_[i1][1] < pts_[i2][1]; });

    // std::stable_sort(indexed_xy.begin(), indexed_xy.end(),
    //                  [](const auto& a, const auto& b) {
    //                    int a_y;
    //                    std::tie(std::ignore, std::ignore, a_y) = a;
    //                    int b_y;
    //                    std::tie(std::ignore, std::ignore, b_y) = b;
    //                    return a_y < b_y;
    //                  });
    tp2 = std::chrono::high_resolution_clock::now();

    // y_sorted_idx.reserve(pts_.size());
    // idx_to_y_order.resize(indexed_xy.size());

    // for (int i = 0; i < indexed_xy.size(); i++) {
    //   int idx;
    //   std::tie(idx, std::ignore, std::ignore) = indexed_xy[i];
    //   idx_to_y_order[idx] = i;
    //   y_sorted_idx.push_back(idx);
    // }

    idx_to_y_order.resize(y_sorted_idx.size());
    for (int i = 0; i < y_sorted_idx.size(); i++) {
      idx_to_y_order[y_sorted_idx[i]] = i;
    }

    end = std::chrono::high_resolution_clock::now();
    td1 = std::chrono::duration_cast<std::chrono::milliseconds>(end - begin)
              .count();

    td3 = std::chrono::duration_cast<std::chrono::milliseconds>(tp0 - begin)
              .count();
    td4 = std::chrono::duration_cast<std::chrono::milliseconds>(tp1 - tp0)
              .count();
    td5 = std::chrono::duration_cast<std::chrono::milliseconds>(tp2 - tp1)
              .count();
    td6 = std::chrono::duration_cast<std::chrono::milliseconds>(end - tp2)
              .count();

    begin = std::chrono::high_resolution_clock::now();

    root = ConstructTree(x_sorted_idx, 0, pts.size() - 1);
    end = std::chrono::high_resolution_clock::now();
    td2 = std::chrono::duration_cast<std::chrono::milliseconds>(end - begin)
              .count();
  }
  Node* ConstructTree(const std::vector<int>& x_sorted_idx_, int y_idx_left,
                      int y_idx_right) {
    // TODO: remove x_sorted_idx_ parameter using y indices
    int y_idx_med = (y_idx_left + y_idx_right + 1) / 2;
    int y_med = pts[y_sorted_idx[y_idx_med]][1];
    int n = x_sorted_idx_.size();
    // std::cout << "Tree Construction [" << y_idx_left << " ~ " << y_idx_right
    //           << "]" << std::endl;
    // std::cout << "y med: " << y_med << std::endl;
    // for (const auto& idx : x_sorted_idx_) {
    //   std::cout << "(" << pts[idx][0] << ", " << pts[idx][1] << ") - ";
    // }
    // std::cout << std::endl;
    Node* node = new Node(y_med, x_sorted_idx_);
    if (y_idx_left == y_idx_right) {
      return node;
    }
    std::vector<int> x_sorted_idx_left;
    x_sorted_idx_left.reserve(n);
    std::vector<int> x_sorted_idx_right;
    x_sorted_idx_right.reserve(n);
    std::vector<int>& left_x_cascading_map = node->left_x_cascading_map;
    left_x_cascading_map.reserve(n);
    std::vector<int>& right_x_cascading_map = node->right_x_cascading_map;
    right_x_cascading_map.reserve(n);
    std::vector<int>& left_x_cascading_map_inverse =
        node->left_x_cascading_map_inverse;
    left_x_cascading_map_inverse.reserve(n);
    std::vector<int>& right_x_cascading_map_inverse =
        node->right_x_cascading_map_inverse;
    right_x_cascading_map_inverse.reserve(n);

    int left_cnt = 0;
    int right_cnt = 0;
    int left_cnt_inverse = -1;
    int right_cnt_inverse = -1;

    // 0~size
    for (int i = 0; i < x_sorted_idx_.size(); i++) {
      left_x_cascading_map.push_back(left_cnt);
      right_x_cascading_map.push_back(right_cnt);

      int y_order_i = idx_to_y_order[x_sorted_idx_[i]];
      if (y_order_i < y_idx_med) {
        x_sorted_idx_left.push_back(x_sorted_idx_[i]);
        left_cnt++;
        left_cnt_inverse++;
      } else {
        x_sorted_idx_right.push_back(x_sorted_idx_[i]);
        right_cnt++;
        right_cnt_inverse++;
      }
      left_x_cascading_map_inverse.push_back(left_cnt_inverse);
      right_x_cascading_map_inverse.push_back(right_cnt_inverse);
    }
    Node* left_node =
        ConstructTree(x_sorted_idx_left, y_idx_left, y_idx_med - 1);
    Node* right_node =
        ConstructTree(x_sorted_idx_right, y_idx_med, y_idx_right);

    node->left = left_node;
    node->right = right_node;
    // node->left_x_cascading_map = left_x_cascading_map;
    // node->right_x_cascading_map = right_x_cascading_map;
    // node->left_x_cascading_map_inverse = left_x_cascading_map_inverse;
    // node->right_x_cascading_map_inverse = right_x_cascading_map_inverse;

    return node;
  }
  int QueryRight(int qx, int qy) const {
    Node* node = root;
    int bound_x_sorted_idx = LowerBound(x_sorted_idx, qx);
    // if (bound_x_sorted_idx < x_sorted_idx.size() &&
    //     x_sorted_idx[bound_x_sorted_idx] == qx) {
    //   bound_x_sorted_idx = UpperBound(x_sorted_idx, qx) + 1;
    // }
    int closest_right_idx = -1;
    while (node->left != nullptr && node->right != nullptr) {
      //   std::cout << "----------------" << std::endl;
      //   std::cout << "y med: " << node->y_med << std::endl;
      //   std::cout << "lower_bound idx: " << bound_x_sorted_idx <<
      //   std::endl; std::cout << "x_sorted_idx : \n\t"; for (const auto& idx :
      //   node->x_sorted_idx) {
      //     std::cout << idx << " ";
      //   }
      //   std::cout << std::endl;

      //   std::cout << "left_cascading_map : \n\t";
      //   for (const auto& cascading_idx : node->left_x_cascading_map) {
      //     std::cout << cascading_idx << " ";
      //   }
      //   std::cout << std::endl;

      //   std::cout << "left->x_sorted_idx : \n\t";
      //   for (const auto& idx : node->left->x_sorted_idx) {
      //     std::cout << idx << " ";
      //   }
      //   std::cout << std::endl;

      //   std::cout << "right_cascading_map : \n\t";
      //   for (const auto& cascading_idx : node->right_x_cascading_map) {
      //     std::cout << cascading_idx << " ";
      //   }
      //   std::cout << std::endl;

      //   std::cout << "right->x_sorted_idx : \n\t";
      //   for (const auto& idx : node->right->x_sorted_idx) {
      //     std::cout << idx << " ";
      //   }
      //   std::cout << std::endl;
      //   std::cout << "left 1, right 0 : " << (qy <= node->y_med) <<
      //   std::endl; std::cout << "closest_right_idx : " << closest_right_idx
      //   << std::endl;

      if (bound_x_sorted_idx >= node->x_sorted_idx.size()) {
        break;
      }

      // NOTE
      // qy 랑 같은 y 에 멈출지 말지? (output sensitive 관련)
      if (qy < node->y_med) {
        int found_higher_x_sorted_idx =
            node->right_x_cascading_map[bound_x_sorted_idx];
        if (found_higher_x_sorted_idx < node->right->x_sorted_idx.size()) {
          int found_higher_idx =
              node->right->x_sorted_idx[found_higher_x_sorted_idx];
          if (closest_right_idx == -1) {
            closest_right_idx = found_higher_idx;
          } else if (pts[found_higher_idx][0] < pts[closest_right_idx][0]) {
            closest_right_idx = found_higher_idx;
          }
        }
        // NOTE else?

        bound_x_sorted_idx = node->left_x_cascading_map[bound_x_sorted_idx];
        node = node->left;

      } else {
        bound_x_sorted_idx = node->right_x_cascading_map[bound_x_sorted_idx];
        node = node->right;
      }
    }
    // NOTE
    // if(closest_right_idx == -1){
    // }
    return closest_right_idx;
  }

  int QueryLeft(int qx, int qy) const {
    Node* node = root;
    int bound_x_sorted_idx = UpperBound(x_sorted_idx, qx) - 1;

    int closest_left_idx = -1;
    while (node->left != nullptr && node->right != nullptr) {
      // std::cout << "----------------" << std::endl;
      // std::cout << "y med: " << node->y_med << std::endl;
      // std::cout << "lower_bound idx: " << bound_x_sorted_idx << std::endl;
      // std::cout << "x_sorted_idx : \n\t";
      // for (const auto& idx : node->x_sorted_idx) {
      //   std::cout << idx << " ";
      // }
      // std::cout << std::endl;

      // std::cout << "left_cascading_map_inverse : \n\t";
      // for (const auto& cascading_idx : node->left_x_cascading_map_inverse) {
      //   std::cout << cascading_idx << " ";
      // }
      // std::cout << std::endl;

      // std::cout << "left->x_sorted_idx : \n\t";
      // for (const auto& idx : node->left->x_sorted_idx) {
      //   std::cout << idx << " ";
      // }
      // std::cout << std::endl;

      // std::cout << "right_cascading_map_inverse : \n\t";
      // for (const auto& cascading_idx : node->right_x_cascading_map_inverse) {
      //   std::cout << cascading_idx << " ";
      // }
      // std::cout << std::endl;

      // std::cout << "right->x_sorted_idx : \n\t";
      // for (const auto& idx : node->right->x_sorted_idx) {
      //   std::cout << idx << " ";
      // }
      // std::cout << std::endl;
      // std::cout << "left 1, right 0 : " << (qy <= node->y_med) << std::endl;
      // std::cout << "closest_left_idx : " << closest_left_idx << std::endl;

      if (bound_x_sorted_idx < 0) {
        break;
      }

      // NOTE
      // qy 랑 같은 y 에 멈출지 말지? (output sensitive 관련)
      if (qy < node->y_med) {
        int found_higher_x_sorted_idx =
            node->right_x_cascading_map_inverse[bound_x_sorted_idx];
        if (found_higher_x_sorted_idx >= 0) {
          int found_higher_idx =
              node->right->x_sorted_idx[found_higher_x_sorted_idx];
          if (closest_left_idx == -1) {
            closest_left_idx = found_higher_idx;
          } else if (pts[found_higher_idx][0] > pts[closest_left_idx][0]) {
            closest_left_idx = found_higher_idx;
          }
        }
        // NOTE else?

        bound_x_sorted_idx =
            node->left_x_cascading_map_inverse[bound_x_sorted_idx];
        node = node->left;

      } else {
        bound_x_sorted_idx =
            node->right_x_cascading_map_inverse[bound_x_sorted_idx];
        node = node->right;
      }
    }
    // NOTE
    // last node consideration?
    if (node->left == nullptr && node->right == nullptr) {
      if (pts[node->x_sorted_idx[0]][0] <= qx &&
          pts[node->x_sorted_idx[0]][1] >= qy) {
        if (closest_left_idx == -1 ||
            pts[node->x_sorted_idx[0]][0] > pts[closest_left_idx][0]) {
          closest_left_idx = node->x_sorted_idx[0];
        }
      }
    }
    return closest_left_idx;
  }
  // x_sorted_idx -> evaluation -> upperbound -> idx
  int UpperBound(const std::vector<int>& x_sorted_idx_, int qx) const {
    int l = 0;
    // not containing end r
    int r = x_sorted_idx_.size();
    while (l < r) {
      int med_idx = (l + r) / 2;
      int med = pts[x_sorted_idx_[med_idx]][0];
      if (med <= qx) {
        l = med_idx + 1;
      } else {
        r = med_idx;
      }
    }
    return l;
  }
  // x_sorted_idx -> evaluation -> lowerbound -> idx
  int LowerBound(const std::vector<int>& x_sorted_idx_, int qx) const {
    int l = 0;
    // not containing end r
    int r = x_sorted_idx_.size();
    while (l < r) {
      int med_idx = (l + r) / 2;
      int med = pts[x_sorted_idx_[med_idx]][0];
      if (med < qx) {
        l = med_idx + 1;
      } else {
        r = med_idx;
      }
    }
    return l;
  }
};

class Solution {
 public:
  // using output-sensitive solution
  std::vector<std::vector<int>> getSkyline(
      std::vector<std::vector<int>>& buildings) {
    std::chrono::high_resolution_clock::time_point begin;
    std::chrono::high_resolution_clock::time_point end;

    std::vector<std::vector<int>> new_buildings;
    begin = std::chrono::high_resolution_clock::now();
    new_buildings = PreprocessBuildings(buildings);
    end = std::chrono::high_resolution_clock::now();
    std::cout << "# preprocess : "
              << std::chrono::duration_cast<std::chrono::milliseconds>(end -
                                                                       begin)
                     .count()
              << std::endl;
    int n = new_buildings.size();

    // starting at 4 too slow
    int h_cnt = 2;

    int h_star = 2;
    // 2, 4, 16, 256 , ...
    std::vector<std::vector<int>> ans;
    while (1) {
      h_star = (1 << (1 << h_cnt++));
      std::vector<std::vector<int>> skyline;
      int k = n / h_star;
      if (h_star * k < n) {
        k++;
      }
      //
      // std::cout << "----- Skyline ----- [ h*: " << h_star << ", k: " << k
      //           << " ]" << std::endl;
      begin = std::chrono::high_resolution_clock::now();

      std::vector<std::vector<std::vector<int>>> subgp_buildings(k);
      for (int i = 0; i < n; i++) {
        int subgp_idx = i / h_star;
        subgp_buildings[subgp_idx].push_back(new_buildings[i]);
      }
      std::vector<std::vector<std::vector<int>>> subgp_skylines;
      subgp_skylines.reserve(k);
      for (int i = 0; i < k; i++) {
        std::chrono::high_resolution_clock::time_point b =
            std::chrono::high_resolution_clock::now();
        subgp_skylines.emplace_back(GetSkylineSlow(subgp_buildings[i]));
        std::chrono::high_resolution_clock::time_point e =
            std::chrono::high_resolution_clock::now();
        // std::cout << "# subgp each skyline : " <<
        // std::chrono::duration_cast<std::chrono::milliseconds>(e - b).count()
        // << std::endl; std::cout << "skyline for subgp " << i << std::endl;
        // for (const auto& pt : subgp_skylines[i]) {
        //   std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
        // }
        // std::cout << std::endl;
      }

      if (k == 1) {
        return subgp_skylines[0];
      }
      end = std::chrono::high_resolution_clock::now();
      std::cout << "# subgp skyline [" << h_star << ", " << k << "]: "
                << std::chrono::duration_cast<std::chrono::milliseconds>(end -
                                                                         begin)
                       .count()
                << std::endl;

      begin = std::chrono::high_resolution_clock::now();
      std::vector<Tree> subgp_trees;
      subgp_trees.reserve(k);
      int sum_td1 = 0, sum_td2 = 0, sum_td3 = 0, sum_td4 = 0, sum_td5 = 0,
          sum_td6 = 0;
      for (int i = 0; i < k; i++) {
        subgp_trees.emplace_back(subgp_skylines[i]);
        sum_td1 += subgp_trees.back().td1;
        sum_td2 += subgp_trees.back().td2;
        sum_td3 += subgp_trees.back().td3;
        sum_td4 += subgp_trees.back().td4;
        sum_td5 += subgp_trees.back().td5;
        sum_td6 += subgp_trees.back().td6;
      }
      end = std::chrono::high_resolution_clock::now();

      std::cout << "# tree construction : "
                << std::chrono::duration_cast<std::chrono::milliseconds>(end -
                                                                         begin)
                       .count()
                << std::endl;
      // std::cout << "# tree construction td1: " << sum_td1 << std::endl;
      // std::cout << "# tree construction td2: " << sum_td2 << std::endl;
      // std::cout << "# tree construction td3: " << sum_td3 << std::endl;
      // std::cout << "# tree construction td4: " << sum_td4 << std::endl;
      // std::cout << "# tree construction td5: " << sum_td5 << std::endl;
      // std::cout << "# tree construction td6: " << sum_td6 << std::endl;

      // merge
      int cur_x = 0;
      int cur_y = 0;
      int cur_subgp_idx = -1;
      int cur_subgp_pt_idx = -1;
      bool succeeded = false;
      // from start point, h_start + 1 iteration needed
      for (int i = 0; i <= h_star; i++) {
        begin = std::chrono::high_resolution_clock::now();
        // std::cout << "- h* loop : " << i << " / " << h_star << std::endl;
        // std::cout << "cur_x: " << cur_x << std::endl
        //           << "cur_y: " << cur_y << std::endl
        //           << "cur_subgp_idx: " << cur_subgp_idx << std::endl
        //           << "cur_subgp_pt_idx: " << cur_subgp_pt_idx << std::endl;
        int next_x, next_y, next_subgp_idx, next_subgp_pt_idx;
        std::tie(next_x, next_y, next_subgp_idx, next_subgp_pt_idx) =
            FindNextSkylinePt(subgp_trees, cur_x, cur_y);
        // std::cout << "next_x: " << next_x << std::endl
        //           << "next_y: " << next_y << std::endl
        //           << "next_subgp_idx: " << next_subgp_idx << std::endl
        //           << "next_subgp_pt_idx: " << next_subgp_pt_idx << std::endl;
        // std::cout
        //     << "Query next response: "
        //     << (cur_subgp_idx == -1 ||
        //         cur_subgp_pt_idx < subgp_trees[cur_subgp_idx].pts.size() - 1)
        //     << (next_x == -1 ||
        //         (cur_subgp_idx != -1 &&
        //          next_x >
        //              subgp_trees[cur_subgp_idx].pts[cur_subgp_pt_idx +
        //              1][0]))
        //     << std::endl;
        if (cur_subgp_idx == -1 ||
            cur_subgp_pt_idx < subgp_trees[cur_subgp_idx].pts.size() - 1) {
          // next subgp pt exists

          if (next_x == -1 ||
              (cur_subgp_idx != -1 &&
               next_x >
                   subgp_trees[cur_subgp_idx].pts[cur_subgp_pt_idx + 1][0])) {
            // no query response
            // if cur_subgp_idx == -1 (init), it must jump
            // to be drop case, next_x must be farther than the cur next x
            // drop to cur_subgp_idx+1 and need to find y
            // assert idx not -1 if no query resp
            int cur_next_x =
                subgp_trees[cur_subgp_idx].pts[cur_subgp_pt_idx + 1][0];
            int cur_next_y =
                subgp_trees[cur_subgp_idx].pts[cur_subgp_pt_idx + 1][1];
            int prev_x, prev_y, prev_subgp_idx, prev_subgp_pt_idx;
            // std::cout << "Query prev: (" << cur_next_x << ", " << cur_next_y
            //           << ")" << std::endl;
            // NOTE: query y?
            std::tie(prev_x, prev_y, prev_subgp_idx, prev_subgp_pt_idx) =
                FindPrevSkylinePt(subgp_trees, cur_next_x, 0, cur_subgp_idx);
            // std::cout << "prev_x: " << prev_x << std::endl
            //           << "prev_y: " << prev_y << std::endl
            //           << "prev_subgp_idx: " << prev_subgp_idx << std::endl
            //           << "prev_subgp_pt_idx: " << prev_subgp_pt_idx
            //           << std::endl;
            // drop to prev y only if it is higher than drop height in the same
            // subgp
            if (prev_y != -1 && prev_y > cur_next_y) {
              cur_x = cur_next_x;
              cur_y = prev_y;
              cur_subgp_idx = prev_subgp_idx;
              cur_subgp_pt_idx = prev_subgp_pt_idx;
            } else {
              // drop to current subgp next pt
              cur_x = cur_next_x;
              cur_y = cur_next_y;
              cur_subgp_pt_idx = cur_subgp_pt_idx + 1;
            }
          } else {
            // jump (move to the query response)
            // including cur subgp.
            cur_x = next_x;
            cur_y = next_y;
            cur_subgp_idx = next_subgp_idx;
            cur_subgp_pt_idx = next_subgp_pt_idx;
          }
        } else {
          // else pt is the last (0,0) of the subgp
          if (next_x == -1) {
            // no query response
            succeeded = true;
            break;
          } else {
            // jump (move to the query response)
            cur_x = next_x;
            cur_y = next_y;
            cur_subgp_idx = next_subgp_idx;
            cur_subgp_pt_idx = next_subgp_pt_idx;
          }
        }
        // std::cout << "-- skyline push : (" << cur_x << ", " << cur_y << ")"
        //           << std::endl;
        skyline.push_back({cur_x, cur_y});
        end = std::chrono::high_resolution_clock::now();

        // std::cout << "# h* loop queary : " <<
        // std::chrono::duration_cast<std::chrono::milliseconds>(end -
        // begin).count() << std::endl;
      }

      if (succeeded) {
        ans = skyline;
        break;
      } else {
        ;  // std::cout << " - fail" << std::endl;
      }

      // h_star = h_star * h_star;
    }

    return ans;
  }
  std::tuple<int, int, int, int> FindNextSkylinePt(
      const std::vector<Tree>& subgp_trees, int qx, int qy) const {
    int next_x = -1;
    int next_y = -1;
    int next_subgp_idx = -1;
    int next_subgp_pt_idx = -1;
    for (int j = 0; j < subgp_trees.size(); j++) {
      const auto& subgp_tree = subgp_trees[j];
      int resp_idx = subgp_tree.QueryRight(qx, qy);
      if (resp_idx > subgp_tree.pts.size()) {
        continue;
      }
      int next_cand_x = subgp_tree.pts[resp_idx][0];
      int next_cand_y = subgp_tree.pts[resp_idx][1];
      if (next_x == -1 || std::pair<int, int>(next_x, -next_y) >
                              std::pair<int, int>(next_cand_x, -next_cand_y)) {
        next_x = next_cand_x;
        next_y = next_cand_y;
        next_subgp_idx = j;
        next_subgp_pt_idx = resp_idx;
      }
    }
    return std::make_tuple(next_x, next_y, next_subgp_idx, next_subgp_pt_idx);
  }

  // regardless x , find highest y value dominating query pt
  // return highest except cur subgp
  std::tuple<int, int, int, int> FindPrevSkylinePt(
      const std::vector<Tree>& subgp_trees, int qx, int qy,
      int cur_subgp_idx) const {
    int prev_x = -1;
    int prev_y = -1;
    int prev_subgp_idx = -1;
    int prev_subgp_pt_idx = -1;
    for (int j = 0; j < subgp_trees.size(); j++) {
      if (j == cur_subgp_idx) {
        continue;
      }
      const auto& subgp_tree = subgp_trees[j];
      int resp_idx = subgp_tree.QueryLeft(qx, qy);
      if (resp_idx > subgp_tree.pts.size()) {
        continue;
      }
      int prev_cand_x = subgp_tree.pts[resp_idx][0];
      int prev_cand_y = subgp_tree.pts[resp_idx][1];
      if (prev_x == -1 || prev_y < prev_cand_y) {
        prev_x = prev_cand_x;
        prev_y = prev_cand_y;
        prev_subgp_idx = j;
        prev_subgp_pt_idx = resp_idx;
      }
    }
    return std::make_tuple(prev_x, prev_y, prev_subgp_idx, prev_subgp_pt_idx);
  }
  // find skyline given building segments in O(n log n)
  std::vector<std::vector<int>> GetSkylineSlow(
      std::vector<std::vector<int>>& buildings) {
    std::vector<std::vector<int>> skyline;
    skyline.reserve(buildings.size() * 2);

    std::vector<std::pair<int, int>> segs;
    segs.reserve(buildings.size());
    for (int i = 0; i < buildings.size(); i++) {
      const auto& b = buildings[i];
      segs.push_back({b[0], i});
      segs.push_back({b[1], i});
    }

    std::sort(segs.begin(), segs.end());

    std::priority_queue<std::pair<int, int>> pq;

    int seg_idx = 0;
    while (seg_idx < segs.size()) {
      int cur_x;
      std::tie(cur_x, std::ignore) = segs[seg_idx];
      while (seg_idx < segs.size() && cur_x == segs[seg_idx].first) {
        int building_idx;
        std::tie(std::ignore, building_idx) = segs[seg_idx];
        const auto& b = buildings[building_idx];
        if (b[0] == cur_x) {
          pq.push({b[2], b[1]});
          // pq.emplace(b[2], b[1]);
        }
        seg_idx++;
      }

      // remove immediately as it ends
      while (!pq.empty() && pq.top().second <= cur_x) {
        pq.pop();
      }
      int cur_height = 0;
      if (!pq.empty()) {
        cur_height = pq.top().first;
      }

      if (skyline.empty() || skyline.back()[1] != cur_height) {
        skyline.push_back({cur_x, cur_height});
      }
    }

    return skyline;
  }

  // remove same height connected buildings
  std::vector<std::vector<int>> PreprocessBuildings(
      std::vector<std::vector<int>>& buildings) {
    std::unordered_map<int, int> um;
    std::vector<std::vector<int>> new_buildings;
    new_buildings.reserve(buildings.size());
    int idx = 0;
    for (const auto& b : buildings) {
      if (um.find(b[2]) == um.end()) {
        new_buildings.push_back(b);
        um[b[2]] = idx++;
      } else {
        // assert um[b[2]] not empty
        auto& last_b = new_buildings[um[b[2]]];
        // intersects
        if (last_b[1] >= b[0]) {
          if (last_b[1] < b[1]) {
            last_b[1] = b[1];
          }
          // contained
        } else {
          // separated
          new_buildings.push_back(b);
          um[b[2]] = idx++;
        }
      }
    }
    return new_buildings;
  }

  void TestTree() {
    std::cout << "===== TestTree =====" << std::endl;
    std::vector<std::vector<int>> pts = {
        {2, 10}, {3, 15}, {5, 12}, {15, 10}, {19, 8}};
    Tree t(pts);
  }
  void TestQuery() {
    std::cout << "===== TestQuery =====" << std::endl;
    std::vector<std::vector<int>> pts = {
        {10, 10}, {8, 15}, {6, 12}, {6, 10},
        {6, 8},   {4, 8},  {2, 8}};
    Tree t(pts);

    std::vector<int> test_list = {6, 5, 4, 3, 2, 1, 0};
    int i;
    i = t.LowerBound(test_list, 5);
    std::cout << "test lowerbound for 5 : " << i << std::endl;
    i = t.LowerBound(test_list, 6);
    std::cout << "test lowerbound for 6 : " << i << std::endl;
    i = t.LowerBound(test_list, 7);
    std::cout << "test lowerbound for 7 : " << i << std::endl;
    i = t.LowerBound(test_list, 0);
    std::cout << "test lowerbound for 0 : " << i << std::endl;
    i = t.LowerBound(test_list, 11);
    std::cout << "test lowerbound for 11 : " << i << std::endl;

    i = t.UpperBound(test_list, 5);
    std::cout << "test upperbound for 5 : " << i << std::endl;
    i = t.UpperBound(test_list, 6);
    std::cout << "test upperbound for 6 : " << i << std::endl;
    i = t.UpperBound(test_list, 7);
    std::cout << "test upperbound for 7 : " << i << std::endl;
    i = t.UpperBound(test_list, 0);
    std::cout << "test upperbound for 0 : " << i << std::endl;
    i = t.UpperBound(test_list, 11);
    std::cout << "test upperbound for 11 : " << i << std::endl;
  }
  void TestQuery2() {
    std::cout << "===== TestQuery2 =====" << std::endl;
    std::vector<std::vector<int>> pts = {
        {2, 14},  {4, 26}, {6, 8},   {8, 4},   {10, 12}, {12, 6},  {14, 20},
        {16, 10}, {18, 2}, {20, 18}, {22, 24}, {24, 16}, {26, 22}, {28, 28}};

    Tree t(pts);

    std::cout << "pts : " << std::endl;
    for (const auto& pt : pts) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;

    std::cout << "y_order : " << std::endl;
    for (const auto& idx : t.x_sorted_idx) {
      std::cout << t.idx_to_y_order[idx] << " ";
    }
    std::cout << std::endl;

    std::vector<std::vector<int>> qs = {
        {9, 5},  {9, 13}, {11, 5}, {11, 13},
        {9, 27}, {9, 28}, {29, 1}, {28, 1},
        {0, 14}, {0, 15}, {15, 1}, {19, 18}};
    for (int i = 0; i < qs.size(); i++) {
      std::cout << "Query : (" << qs[i][0] << ", " << qs[i][1]
                << ") : " << std::endl;
      int qidx = t.QueryRight(qs[i][0], qs[i][1]);
      if (qidx != -1) {
        std::cout << qidx << " => "
                  << "(" << pts[qidx][0] << ", " << pts[qidx][1] << ")"
                  << std::endl;
      } else {
        std::cout << qidx << " => not found" << std::endl;
      }
    }
  }

  void TestQuery3() {
    std::cout << "===== TestQuery3 =====" << std::endl;
    std::vector<std::vector<int>> pts = {
        {2, 14},  {4, 26},  {6, 8},   {8, 4},
        {10, 12}, {12, 6},  {14, 20}, {16, 10},
        {18, 2},  {20, 18}, {22, 24}, {24, 16},
        {26, 22}, {28, 28}, {30, 0}};

    Tree t(pts);

    std::cout << "pts : " << std::endl;
    for (const auto& pt : pts) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;

    std::cout << "y_order : " << std::endl;
    for (const auto& idx : t.x_sorted_idx) {
      std::cout << t.idx_to_y_order[idx] << " ";
    }
    std::cout << std::endl;

    std::vector<std::vector<int>> qs = {
        {9, 5},   {9, 13}, {11, 5},  {11, 13},
        {9, 27},  {9, 28}, {29, 1},  {28, 1},
        {0, 14},  {0, 15}, {15, 1},  {19, 18},
        {28, 28}, {2, 14}, {26, 22}, {31, 0}};
    for (int i = 0; i < qs.size(); i++) {
      std::cout << "Query : (" << qs[i][0] << ", " << qs[i][1]
                << ") : " << std::endl;
      int qidx = t.QueryLeft(qs[i][0], qs[i][1]);
      if (qidx != -1) {
        std::cout << qidx << " => "
                  << "(" << pts[qidx][0] << ", " << pts[qidx][1] << ")"
                  << std::endl;
      } else {
        std::cout << qidx << " => not found" << std::endl;
      }
    }
  }
  void TestSlow() {
    std::cout << "===== TestSlow =====" << std::endl;
    std::vector<std::vector<int>> buildings = {
        {2, 9, 10}, {3, 7, 15}, {5, 12, 12}, {15, 20, 10}, {19, 24, 8}};
    std::vector<std::vector<int>> ans;
    ans = GetSkylineSlow(buildings);
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }

  void TestSlow2() {
    std::cout << "===== TestSlow2 =====" << std::endl;
    std::vector<std::vector<int>> buildings;
    int n = 10;
    for (int i = 1; i <= n; i++) {
      buildings.push_back({i, 2 * n - i + 1, i});
    }
    std::vector<std::vector<int>> ans;
    ans = GetSkylineSlow(buildings);
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }

  void TestSlow3() {
    std::cout << "===== TestSlow3 =====" << std::endl;
    std::vector<std::vector<int>> buildings;
    int n = 30;
    for (int i = 1; i <= n; i++) {
      if (i % 3 != 0) {
        buildings.push_back({i, i + 1, 2});
      }
    }
    std::vector<std::vector<int>> ans;
    ans = GetSkylineSlow(buildings);
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }
  void TestSkyline() {
    std::cout << "===== TestSkyline =====" << std::endl;
    std::vector<std::vector<int>> buildings = {
        {2, 9, 10}, {3, 7, 15}, {5, 12, 12}, {15, 20, 10}, {19, 24, 8}};
    std::vector<std::vector<int>> ans;
    ans = getSkyline(buildings);
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }

  void TestSkyline2() {
    std::cout << "===== TestSkyline2 =====" << std::endl;
    std::vector<std::vector<int>> buildings;
    int n = 100;
    for (int i = 1; i <= n; i++) {
      buildings.push_back({i + 1, 2 * n - i + 2, i});
    }
    buildings.push_back({1, 202, 101});
    std::vector<std::vector<int>> ans;
    ans = getSkyline(buildings);
    std::cout << "----- Result -----" << std::endl;
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }

  void TestSkyline3() {
    std::cout << "===== TestSkyline3 =====" << std::endl;
    std::vector<std::vector<int>> buildings;
    int n = 30;
    for (int i = 1; i <= n; i++) {
      if (i % 3 != 0) {
        buildings.push_back({i, i + 1, 2});
      }
    }
    std::vector<std::vector<int>> ans;
    ans = getSkyline(buildings);
    std::cout << "----- Result -----" << std::endl;
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }

  void TestSkyline4() {
    std::cout << "===== TestSkyline4 =====" << std::endl;
    std::vector<std::vector<int>> buildings = {
        {1, 2, 1}, {1, 2, 2}, {1, 2, 3},
        {2, 3, 1}, {2, 3, 2}, {2, 3, 3}};
    std::vector<std::vector<int>> ans;
    ans = getSkyline(buildings);
    std::cout << "----- Result -----" << std::endl;
    for (const auto& pt : ans) {
      std::cout << "(" << pt[0] << ", " << pt[1] << ") - ";
    }
    std::cout << std::endl;
  }

  void TestSkyline5() {
    std::cout << "===== TestSkyline5 =====" << std::endl;
    std::vector<std::vector<int>> buildings = {
        {1, 38, 219},  {2, 19, 228},  {2, 64, 106},  {3, 80, 65},
        {3, 84, 8},    {4, 12, 8},    {4, 25, 14},   {4, 46, 225},
        {4, 67, 187},  {5, 36, 118},  {5, 48, 211},  {5, 55, 97},
        {6, 42, 92},   {6, 56, 188},  {7, 37, 42},   {7, 49, 78},
        {7, 84, 163},  {8, 44, 212},  {9, 42, 125},  {9, 85, 200},
        {9, 100, 74},  {10, 13, 58},  {11, 30, 179}, {12, 32, 215},
        {12, 33, 161}, {12, 61, 198}, {13, 38, 48},  {13, 65, 222},
        {14, 22, 1},   {15, 70, 222}, {16, 19, 196}, {16, 24, 142},
        {16, 25, 176}, {16, 57, 114}, {18, 45, 1},   {19, 79, 149},
        {20, 33, 53},  {21, 29, 41},  {23, 77, 43},  {24, 41, 75},
        {24, 94, 20},  {27, 63, 2},   {31, 69, 58},  {31, 88, 123},
        {31, 88, 146}, {33, 61, 27},  {35, 62, 190}, {35, 81, 116},
        {37, 97, 81},  {38, 78, 99},  {39, 51, 125}, {39, 98, 144},
        {40, 95, 4},   {45, 89, 229}, {47, 49, 10},  {47, 99, 152},
        {48, 67, 69},  {48, 72, 1},   {49, 73, 204}, {49, 77, 117},
        {50, 61, 174}, {50, 76, 147}, {52, 64, 4},   {52, 89, 84},
        {54, 70, 201}, {57, 76, 47},  {58, 61, 215}, {58, 98, 57},
        {61, 95, 190}, {66, 71, 34},  {66, 99, 53},  {67, 74, 9},
        {68, 97, 175}, {70, 88, 131}, {74, 77, 155}, {74, 99, 145},
        {76, 88, 26},  {82, 87, 40},  {83, 84, 132}, {88, 99, 99}};
    std::vector<std::vector<int>> ans;
    ans = getSkyline(buildings);
    std::cout << "----- Result -----" << std::endl;
    for (const auto& pt : ans) {
      std::cout << "[" << pt[0] << ", " << pt[1] << "], ";
    }
    std::cout << std::endl;
  }

  void TestSkyline6() {
    std::cout << "===== TestSkyline6 =====" << std::endl;
    std::ifstream infile("test_input");
    std::vector<std::vector<int>> buildings;
    int x1, x2, y;
    while (!infile.eof()) {
      infile >> x1 >> x2 >> y;
      buildings.push_back({x1, x2, y});
    }
    std::cout << "input length: " << buildings.size() << std::endl;

    std::vector<std::vector<int>> ans;
    ans = getSkyline(buildings);
    std::cout << "----- Result -----" << std::endl;
    for (const auto& pt : ans) {
      std::cout << "[" << pt[0] << ", " << pt[1] << "], ";
    }
    std::cout << std::endl;
  }
  std::vector<std::vector<int>> GenerateRandomInput(int n, std::mt19937& gen) {
    std::uniform_int_distribution<int> dist_x(1, 1 << 20);
    std::uniform_int_distribution<int> dist_y(1, 1 << 20);
    std::vector<std::vector<int>> buildings(n);
    for (int i = 0; i < n; i++) {
      int x1, x2, y;
      x1 = dist_x(gen);
      x2 = dist_x(gen);
      y = dist_y(gen);
      if (x1 > x2) {
        int tmp = x1;
        x1 = x2;
        x2 = tmp;
      } else if (x1 == x2) {
        x2 = x1 + 1;
      }
      buildings[i] = {x1, x2, y};
    }
    std::sort(buildings.begin(), buildings.end());
    return buildings;
  }
  void ProfileTC() {
    int repetition = 2;
    std::random_device rd;
    std::mt19937 gen(1234);  // rd()
    std::stringstream ss;
    std::ofstream outfile("profile");
    int scale = 20000000;
    for (int n = scale; n <= scale * 1; n = n + scale / 2) {
      for (int i = 0; i < repetition; i++) {
        std::vector<std::vector<int>> buildings = GenerateRandomInput(n, gen);
        std::chrono::high_resolution_clock::time_point begin;
        std::chrono::high_resolution_clock::time_point end;
        std::vector<std::vector<int>> ans;
        begin = std::chrono::high_resolution_clock::now();
        ans = GetSkylineSlow(buildings);
        end = std::chrono::high_resolution_clock::now();

        int h1 = ans.size();
        auto time_ms1 =
            std::chrono::duration_cast<std::chrono::milliseconds>(end - begin)
                .count();

        begin = std::chrono::high_resolution_clock::now();
        ans = getSkyline(buildings);
        end = std::chrono::high_resolution_clock::now();
        int h2 = ans.size();
        auto time_ms2 =
            std::chrono::duration_cast<std::chrono::milliseconds>(end - begin)
                .count();
        int h = -1;
        if (h1 == h2) {
          h = h1;
        } else {
          outfile << "----- Error ----- : " << h1 << " vs " << h2 << std::endl;
          for (const auto& b : buildings) {
            outfile << b[0] << " " << b[1] << " " << b[2] << std::endl;
          }
          return;
        }

        outfile << n << " " << h << " " << time_ms1 << " " << time_ms2
                << std::endl;
      }
    }
    // outfile << ss.rdbuf();
  }
};

int main() {
  Solution s;
  // s.TestTree();
  // s.TestQuery();
  // s.TestQuery2();
  // s.TestQuery3();
  // s.TestSlow();
  // s.TestSlow2();
  // s.TestSlow3();
  // s.TestSkyline();
  // s.TestSkyline2();
  // s.TestSkyline3();
  // s.TestSkyline4();
  // s.TestSkyline5();
  // s.TestSkyline6();
  s.ProfileTC();
  return 0;
}
{% endhighlight %}
</details>  



<details>
<summary>시각화 코드</summary>

{% highlight python %}
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

# 10^4
def generate_random_case(n):
    # buildings = [[1,2**5, 2**5]]
    buildings = []
    x_max = 2 ** 10
    y_max = 2 ** 10
    for i in range(n):
        x1, x2, y = np.random.randint(1, [x_max, x_max, y_max])
        if x1 > x2: 
            x1,x2 = x2, x1
        elif x1 == x2:
            x2 = x2+1
        buildings.append([x1, x2, y])
    buildings = sorted(buildings)
    return buildings

if __name__ == "__main__":
    np.random.seed(2)
    fig, ax = plt.subplots()

    

    # buildings = [[1,38,219],[2,19,228],[2,64,106],[3,80,65],[3,84,8],[4,12,8],[4,25,14],[4,46,225],[4,67,187],[5,36,118],[5,48,211],[5,55,97],[6,42,92],[6,56,188],[7,37,42],[7,49,78],[7,84,163],[8,44,212],[9,42,125],[9,85,200],[9,100,74],[10,13,58],[11,30,179],[12,32,215],[12,33,161],[12,61,198],[13,38,48],[13,65,222],[14,22,1],[15,70,222],[16,19,196],[16,24,142],[16,25,176],[16,57,114],[18,45,1],[19,79,149],[20,33,53],[21,29,41],[23,77,43],[24,41,75],[24,94,20],[27,63,2],[31,69,58],[31,88,123],[31,88,146],[33,61,27],[35,62,190],[35,81,116],[37,97,81],[38,78,99],[39,51,125],[39,98,144],[40,95,4],[45,89,229],[47,49,10],[47,99,152],[48,67,69],[48,72,1],[49,73,204],[49,77,117],[50,61,174],[50,76,147],[52,64,4],[52,89,84],[54,70,201],[57,76,47],[58,61,215],[58,98,57],[61,95,190],[66,71,34],[66,99,53],[67,74,9],[68,97,175],[70,88,131],[74,77,155],[74,99,145],[76,88,26],[82,87,40],[83,84,132],[88,99,99]]
    buildings = generate_random_case(20)
    # print(buildings)
    with open("test_input_py", "w", encoding="utf-8") as f:
        f.write(str(buildings))
    with open("test_input", "w", encoding="utf-8") as f:
        for b in buildings:
            f.write(f"{b[0]} {b[1]} {b[2]}\n")

    print(len(buildings))

    
    x_max = max([b[1] for b in buildings])
    y_max = max([b[2] for b in buildings])

    ax.set_xlim([-1, x_max*1.1])
    ax.set_ylim([-1, y_max*1.1])
    # ax.set_xticks(np.arange(-1, x_max, 100))

    cmap = plt.cm.viridis

    for b in buildings:
        ax.add_patch(Rectangle((b[0], 0), b[1]-b[0], b[2],
                fill=False,
                lw=1, 
                color=cmap(np.random.rand(1))))

    # ans = [[1, 219], [2, 228], [19, 225], [45, 229], [89, 190], [95, 175], [97, 152], [99, 74], [100, 0]]
    ans  = [[32, 451], [103, 773], [196, 494], [360, 1003], [551, 893], [562, 943], [808, 288], [832, 133], [973, 0]]

    ans_x = [pt[0] for pt in ans]
    ans_y = [pt[1] for pt in ans]
    ax.scatter(ans_x, ans_y, c='red')

    plt.show()
{% endhighlight %}
</details>  



