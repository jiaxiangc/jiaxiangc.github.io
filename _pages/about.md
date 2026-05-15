---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>

I am a Researcher at **Tencent HY**, working with [Heng Wang](https://scholar.google.com/citations?user=ghmgyewAAAAJ&hl=en) in the Video World Model Team. Previously, I worked with [Qinglin Lu](https://openreview.net/profile?id=~Qinglin_Lu2) in the Video Application Team, and was a Research Intern at **ByteDance Intelligent Creation Team**, collaborating with [Jie Wu](https://scholar.google.com/citations?user=MxvLqLcAAAAJ&hl=zh-CN) and [Pan Xie](https://scholar.google.com/citations?user=Z-0EqtgAAAAJ&hl=en). I received my Master degree in Artificial Intelligence from Beihang University (2025).

I am currently exploring **Video World Models**. My research interests center on **Diffusion Distillation** and **Preference Alignment**. Welcome to discuss, feel free to reach out at <a href="mailto:jiaxiangcc@gmail.com">jiaxiangcc@gmail.com</a>.


# 🔥 News
- *2026.05*: &nbsp;🎉 One paper about preference alignment is accepted in <span style="color:#224b8d; font-weight:bold;">ICML 2026</span>.
- *2025.10*: &nbsp;🎉 One paper about video diffusion acceleration is accepted in <span style="color:#224b8d; font-weight:bold;">AAAI 2026</span>.
- *2024.11*: &nbsp;🏢 Joined <img src="images/tencent_logo.svg" alt="Tencent" style="height:1.2em; vertical-align:middle;"> **Tencent HY** as Researcher.
- *2024.11*: &nbsp;🎉 One paper about resolution adapter is accepted in <span style="color:#224b8d; font-weight:bold;">AAAI 2025</span>.
- *2023.04*: &nbsp;🏢 Joined <img src="images/bytedance_logo.svg" alt="ByteDance" style="height:1.2em; vertical-align:middle;"> **ByteDance Intelligent Creation** as Research Intern.

# 📝 Recent Works

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">arXiv 2026</div><img src='images/faithfulfaces.png' alt="sym" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[FaithfulFaces: Pose-Faithful Facial Identity Preservation for Text-to-Video Generation](https://arxiv.org/abs/2605.04702)

Yuanzhi Wang, Xuhua Ren, **Jiaxiang Cheng**, Bing Ma, Kai Yu, Sen Liang, Wenyue Li, Tianxiang Zheng, Qinglin Lu, Zhen Cui

<a href="https://arxiv.org/abs/2605.04702"><img src="https://img.shields.io/badge/Project-Page-blue?style=flat-square&logo=googlechrome&logoColor=white"></a> <a href="https://arxiv.org/abs/2605.04702"><img src="https://img.shields.io/badge/arXiv-2605.04702-b31b1b?style=flat-square&logo=arxiv&logoColor=white"></a>
- A pose-faithful approach for preserving facial identity in text-to-video generation.
</div>
</div>

# 📝 Publications 

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ICML 2026</div><img src='images/ipa.png' alt="sym" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[Implicit Preference Alignment for Human Image Animation](https://arxiv.org/abs/2605.07545) <span style="background:#c0392b; color:white; padding:1px 6px; border-radius:3px; font-size:0.8em; font-weight:bold;">CCF-A</span>

Yuanzhi Wang, Xuhua Ren, **Jiaxiang Cheng**, Bing Ma, Kai Yu, Tianxiang Zheng, Qinglin Lu, Zhen Cui

<a href="https://arxiv.org/abs/2605.07545"><img src="https://img.shields.io/badge/Project-Page-blue?style=flat-square&logo=googlechrome&logoColor=white"></a> <a href="https://arxiv.org/abs/2605.07545"><img src="https://img.shields.io/badge/arXiv-2605.07545-b31b1b?style=flat-square&logo=arxiv&logoColor=white"></a>
- A preference alignment framework for human image animation that eliminates the need for paired preference data.
</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">AAAI 2026</div><img src='images/phased_oae.png' alt="sym" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[Phased One-step Adversarial Equilibrium for Video Diffusion Models](https://arxiv.org/abs/2508.21019) <span style="background:#c0392b; color:white; padding:1px 6px; border-radius:3px; font-size:0.8em; font-weight:bold;">CCF-A</span>

**Jiaxiang Cheng**, Bing Ma, Xuhua Ren, Hongyi Henry Jin, Kai Yu, Peng Zhang, Wenyue Li, Yuan Zhou, Tianxiang Zheng, Qinglin Lu

<a href="https://arxiv.org/abs/2508.21019"><img src="https://img.shields.io/badge/Project-Page-blue?style=flat-square&logo=googlechrome&logoColor=white"></a> <a href="https://arxiv.org/abs/2508.21019"><img src="https://img.shields.io/badge/Code-GitHub-black?style=flat-square&logo=github"></a> <a href="https://arxiv.org/abs/2508.21019"><img src="https://img.shields.io/badge/arXiv-2508.21019-b31b1b?style=flat-square&logo=arxiv&logoColor=white"></a>
- A novel phased adversarial training framework for one-step video generation with diffusion models.
</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">AAAI 2025</div><img src='images/resadapter.png' alt="sym" width="100%"></div></div>
<div class='paper-box-text' markdown="1">

[ResAdapter: Domain Consistent Resolution Adapter for Diffusion Models](https://arxiv.org/abs/2403.02084) <span style="background:#c0392b; color:white; padding:1px 6px; border-radius:3px; font-size:0.8em; font-weight:bold;">CCF-A</span>

**Jiaxiang Cheng**, Pan Xie, Xin Xia, Jiashi Li, Jie Wu, Yuxi Ren, Huixia Li, Xuefeng Xiao, Min Zheng, Lean Fu

<a href="https://github.com/bytedance/res-adapter"><img src="https://img.shields.io/badge/Project-Page-blue?style=flat-square&logo=googlechrome&logoColor=white"></a> <a href="https://github.com/bytedance/res-adapter"><img src="https://img.shields.io/badge/Code-GitHub-black?style=flat-square&logo=github"></a> <a href="https://arxiv.org/abs/2403.02084"><img src="https://img.shields.io/badge/arXiv-2403.02084-b31b1b?style=flat-square&logo=arxiv&logoColor=white"></a> <a href="https://github.com/bytedance/res-adapter"><img src="https://img.shields.io/badge/GitHub%20Stars-765-yellow?style=flat-square&logo=github"></a>
- A plug-and-play resolution adapter for diffusion models that enables arbitrary resolution generation without retraining.
</div>
</div>

- [HunyuanVideo: A Systematic Framework for Large Video Generative Models](https://arxiv.org/abs/2412.03603), Weijie Kong, Qi Tian, Zijian Zhang, Rox Min, Zuozhuo Dai, ..., **Jiaxiang Cheng**, et al., **arXiv 2024** \| <a href="https://github.com/Tencent/HunyuanVideo"><img src="https://img.shields.io/badge/GitHub%20Stars-12k-yellow?style=flat-square&logo=github"></a>
- [Hunyuan-Game: Industrial-grade Intelligent Game Creation Model](https://arxiv.org/abs/2505.14135), Ruihuang Li, Caijin Zhou, Shoujian Zheng, Jianxiang Lu, Jiabin Huang, Comi Chen, Junshu Tang, Guangzheng Xu, Jiale Tao, **Jiaxiang Cheng**, et al., **arXiv 2025**
- [Beyond Reward Margin: Rethinking and Resolving Likelihood Displacement in Diffusion Models via Video Generation](https://arxiv.org/abs/2511.19049), Ruojun Xu, Yu Kai, Xuhua Ren, **Jiaxiang Cheng**, Bing Ma, Tianxiang Zheng, Qinglin Lu, **arXiv 2025**
- [PersonaVlog: Personalized Multimodal Vlog Generation with Multi-Agent Collaboration and Iterative Self-Correction](https://arxiv.org/abs/2508.13602), Xiaolu Hou, Bing Ma, **Jiaxiang Cheng**, Xuhua Ren, Kai Yu, Wenyue Li, Tianxiang Zheng, Qinglin Lu, **arXiv 2025**

# 📖 Educations
- *2022.09 - 2025.06*, M.S. in Artificial Intelligence, Beihang University, Beijing, China. 
- *2018.09 - 2022.06*, B.E. in Automation, Xidian University, Xi'an, China. 

# 💻 Experience
- *2024.11 - Present*, Researcher, <img src="images/tencent_logo.svg" alt="Tencent" style="height:1.2em; vertical-align:middle;"> Tencent HY, Beijing, China.
- *2023.04 - 2024.10*, Research Intern, <img src="images/bytedance_logo.svg" alt="ByteDance" style="height:1.2em; vertical-align:middle;"> ByteDance Intelligent Creation, Beijing, China.
