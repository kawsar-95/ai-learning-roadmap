# Video coverage

Which YouTube videos the Parts list, which technical topics the site does not cover yet, and where each clip came from. Generated 2026-11-06 from the same data the site reads. Every id was found from a published title, never typed. Each clip on a page was checked live against YouTube before it went into `src/content/`: oEmbed (public and embeddable), the Shorts redirect (a Short really is one), and the IFrame player (it starts, and its length is the real one). The gap-list resources below got the first two checks, because the site does not embed them. Views are rounded and were read from each channel's listing on that day.

## Channels

| Channel | Handle | Listed (videos / Shorts) | Added to the Parts (videos / Shorts) |
| --- | --- | --- | --- |
| KodeKloud | `@KodeKloud` | 561 / 752 | 33 / 57 |
| Cole Medin | `@ColeMedin` | 231 / 63 | 10 / 3 |
| AI Jason | `@AIJasonZ` | 103 / 0 | 6 / 0 |
| Krish Naik | `@krishnaik06` | 1,500+ / 55 | 16 / 0 |
| David Ondrej | `@DavidOndrej` | 399 / 204 | 3 / 0 |
| TechWorld with Nana | `@TechWorldwithNana` | 164 / 23 | 1 / 0 |
| Lucas Soares \| Automata Learning Lab | `@automatalearninglab` | 123 / 156 | 2 / 0 |
| DeepLearningAI | `@Deeplearningai` | 584 / 38 | 3 / 1 |

Krish Naik's list stops at the newest 1,500 videos, a cap set for the crawl, so his older videos were not searched.

135 clips were added to 39 sections; 89 more were read and left out, each with its reason in [video-review-log.md](video-review-log.md).

## Topics the site does not cover yet

KodeKloud and TechWorld with Nana publish courses on all of these, which is where the lists below come from, but the 16 Parts have little or no reference page for them. The counts are rough keyword hits, not a judgement of quality: a topic with many roadmap lessons but no Part reference can be attached to those lessons once the roadmap schema allows videos (it does not today). The lists put the most viewed first. They are suggestions to review before any of them becomes a Part or a section, and the site does not embed them.

### Docker & containers

**On the site today:** 16 keyword hits in 5 of the 16 Parts, and 76 roadmap lessons mention it. **Suggested addition:** Packaging models and apps in containers: images, volumes, GPU passthrough, Compose for a RAG stack.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Docker Tutorial for Beginners [FULL COURSE in 3 Hours]](https://www.youtube.com/watch?v=3c-iBn73dDE) | TechWorld with Nana | 2:46:15 | 6.5M |
| [Docker Crash Course for Absolute Beginners [NEW]](https://www.youtube.com/watch?v=pg19Z8LL06w) | TechWorld with Nana | 1:07:39 | 3.1M |
| [Learn Docker in 2 Hours - A Full Tutorial (2025)](https://www.youtube.com/watch?v=zJ6WbK9zFpI) | KodeKloud | 2:09:28 | 1.1M |
| [What is Docker? Docker container concept explained \|\| Docker Tutorial 1](https://www.youtube.com/watch?v=jPdIRX6q4jA) | TechWorld with Nana | 10:44 | 507K |
| [Docker vs Podman, Explained](https://www.youtube.com/shorts/OM3LfuQRL3s) | KodeKloud | Short | 112K |
| [Docker 101: A Beginner's Guide to Containerization](https://www.youtube.com/watch?v=wxxigbHwDGM) | KodeKloud | 11:03 | 98K |
| [Containers vs Virtual Machines Explained](https://www.youtube.com/shorts/biDEGt6XWc4) | KodeKloud | Short | 66K |
| [How to Use a .dockerignore File Properly](https://www.youtube.com/shorts/IiUY9kqAyRg) | KodeKloud | Short | 39K |

### Kubernetes (and AI on Kubernetes)

**On the site today:** 125 keyword hits in 11 of the 16 Parts, and 170 roadmap lessons mention it. **Suggested addition:** Serving LLMs on a cluster: Deployments and Services, GPU scheduling, autoscaling, operators.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Kubernetes Tutorial for Beginners [FULL COURSE in 4 Hours]](https://www.youtube.com/watch?v=X48VuDVv0do) | TechWorld with Nana | 3:36:55 | 10.0M |
| [Kubernetes Crash Course for Absolute Beginners [NEW]](https://www.youtube.com/watch?v=s_o8dwzRlu4) | TechWorld with Nana | 1:12:04 | 3.9M |
| [What is Kubernetes \| Kubernetes explained in 15 mins](https://www.youtube.com/watch?v=VnvRFRk_51k) | TechWorld with Nana | 14:13 | 1.5M |
| [Kubernetes Crash Course: Learn the Basics and Build a Microservice Application](https://www.youtube.com/watch?v=XuSQU5Grv1g) | KodeKloud | 2:10:00 | 1.2M |
| [What is Helm in Kubernetes? Helm and Helm Charts explained \| Kubernetes Tutorial 23](https://www.youtube.com/watch?v=-ykwb1d0DXU) | TechWorld with Nana | 14:16 | 1.0M |
| [What Is Kubernetes - The Engine Behind Google's massive Container Systems \| KodeKloud](https://www.youtube.com/watch?v=QJ4fODH6DXI) | KodeKloud | 9:50 | 828K |
| [Kubernetes Services explained \| ClusterIP vs NodePort vs LoadBalancer vs Headless Service](https://www.youtube.com/watch?v=T4Z7visMM4E) | TechWorld with Nana | 24:13 | 692K |
| [AI Infrastructure Explained (GPUs, vLLM, and LLM-D)](https://www.youtube.com/watch?v=hBzUokVYQkI) | KodeKloud | 50:59 | 434K |
| [Kubernetes Architecture Simplified \| K8s Explained in 10 Minutes \| KodeKloud](https://www.youtube.com/watch?v=8C_SCDbUJTg) | KodeKloud | 9:31 | 367K |
| [Kubernetes Operator simply explained in 10 mins](https://www.youtube.com/watch?v=ha3LjlD6g7g) | TechWorld with Nana | 10:09 | 311K |
| [Kubernetes Explained Without the Jargon!](https://www.youtube.com/shorts/f44s063zOrQ) | KodeKloud | Short | 65K |
| [How To Upgrade Kubernetes Without Downtime](https://www.youtube.com/shorts/jfRxw5-Gdq8) | KodeKloud | Short | 56K |
| [How to Deploy an AI Agent in Kubernetes (Kagent)](https://www.youtube.com/shorts/CeOsIjO0gzk) | KodeKloud | Short, 2:25 | 25K |

### CI/CD and GitOps

**On the site today:** 1 keyword hits in 1 of the 16 Parts, and 11 roadmap lessons mention it. **Suggested addition:** Gate prompt, model and eval changes in a pipeline, and deploy with GitOps.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [GitHub Actions Tutorial - Basic Concepts and CI/CD Pipeline with Docker](https://www.youtube.com/watch?v=R8_veQiYBjI) | TechWorld with Nana | 32:31 | 2.3M |
| [GitLab CI CD Tutorial for Beginners [Crash Course]](https://www.youtube.com/watch?v=qP8kir2GUgo) | TechWorld with Nana | 1:09:00 | 1.8M |
| [ArgoCD Tutorial for Beginners \| GitOps CD for Kubernetes](https://www.youtube.com/watch?v=MeU5_k9ssrs) | TechWorld with Nana | 47:53 | 954K |
| [Complete Jenkins Pipeline Tutorial \| Jenkinsfile explained](https://www.youtube.com/watch?v=7KCS70sCoK0) | TechWorld with Nana | 35:06 | 933K |
| [CI/CD Explained: The DevOps Skill That Makes You 10x More Valuable](https://www.youtube.com/watch?v=AknbizcLq4w) | TechWorld with Nana | 21:07 | 589K |
| [What is GitOps, How GitOps works and Why it's so useful](https://www.youtube.com/watch?v=f5EpcWp0THw) | TechWorld with Nana | 11:33 | 472K |
| [DevOps: CI/CD Introduction (Continuous Integration, Continuous Delivery, Continuous Deployment)](https://www.youtube.com/watch?v=AlrImm1T8Wg) | KodeKloud | 4:09 | 109K |
| [Demystifying GitOps: A Beginner-Friendly Explanation \| KodeKloud](https://www.youtube.com/watch?v=GlG6Xr2HH1g) | KodeKloud | 8:01 | 49K |
| [Complete Jenkins Pipeline Tutorial \| Jenkinsfile explained \| KodeKloud](https://www.youtube.com/watch?v=EzgCoOQvOf0) | KodeKloud | 30:13 | 44K |
| [GitHub Actions Tutorial: Advanced Concepts You Should Know (Part 1)](https://www.youtube.com/watch?v=E2RRxcq_08E) | KodeKloud | 1:28:57 | 35K |
| [Best CI/CD Tools in 2026](https://www.youtube.com/shorts/17sw0ygRzQE) | KodeKloud | Short | 28K |
| [6 GitOps Advantages Every Engineer Should Know](https://www.youtube.com/shorts/cE6NjiSycT0) | KodeKloud | Short | 27K |
| [What is GitHub Actions? - Everything you need to know to get started](https://www.youtube.com/watch?v=jtKrINOzQ3A) | KodeKloud | 9:21 | 17K |

### Infrastructure as Code

**On the site today:** 0 keyword hits in 0 of the 16 Parts, and 1 roadmap lessons mention it. **Suggested addition:** Provision GPU nodes, vector databases and networks with Terraform or Pulumi; configure with Ansible.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Terraform explained in 15 mins \| Terraform Tutorial for Beginners](https://www.youtube.com/watch?v=l5k1ai_GBDE) | TechWorld with Nana | 18:15 | 2.2M |
| [What is Ansible \| Ansible Playbook explained \| Ansible Tutorial for Beginners](https://www.youtube.com/watch?v=1id6ERvfozo) | TechWorld with Nana | 16:41 | 951K |
| [Terraform Tutorial for Beginners + Labs: Complete Step by Step Guide!](https://www.youtube.com/watch?v=YcJ9IeukJL8) | KodeKloud | 1:55:06 | 871K |
| [8 Terraform Best Practices that will improve your TF workflow immediately](https://www.youtube.com/watch?v=gxPykhPxRW0) | TechWorld with Nana | 8:57 | 272K |
| [What is Infrastructure as Code? Difference of Infrastructure as Code Tools](https://www.youtube.com/watch?v=POPP2WTJ8es) | TechWorld with Nana | 8:04 | 240K |
| [Ansible Playbook for Beginners: Quick 10-Minute Guide](https://www.youtube.com/watch?v=Z01b9QZG0D0) | KodeKloud | 8:16 | 169K |
| [Pulumi - IaC in your favorite programming language!](https://www.youtube.com/watch?v=vIjeiDcsR3Q) | TechWorld with Nana | 19:41 | 129K |
| [Crossplane vs Terraform: What's the Real Difference?](https://www.youtube.com/shorts/jKipg6vA3mE) | KodeKloud | Short | 33K |
| [Pulumi Tutorial: Introduction, Benefits, and Demo of Modern Infrastructure as Code](https://www.youtube.com/watch?v=IuF0GlO2Myk) | KodeKloud | 35:23 | 30K |
| [What is Terraform? \| Introduction To Terraform Basics \| KodeKloud](https://www.youtube.com/watch?v=mzgfHmDRamk) | KodeKloud | 23:38 | 24K |
| [The Best Infrastructure as Code Tool](https://www.youtube.com/shorts/dRaipDwap8A) | KodeKloud | Short | 10K |

### Cloud platforms and managed AI services

**On the site today:** 21 keyword hits in 6 of the 16 Parts, and 111 roadmap lessons mention it. **Suggested addition:** Bedrock, Vertex AI and Azure OpenAI side by side, plus IAM, networking and cost basics.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Stop Watching AWS Tutorials! Build This Instead (Free Labs Included)](https://www.youtube.com/watch?v=7eP8U2CnKdA) | KodeKloud | 21:39 | 1.1M |
| [AWS EKS - Create Kubernetes cluster on Amazon EKS \| the easy way](https://www.youtube.com/watch?v=p6xDCz00TxU) | TechWorld with Nana | 16:27 | 672K |
| [Containers on AWS Overview: ECS \| EKS \| Fargate \| ECR](https://www.youtube.com/watch?v=AYAh6YDXuho) | TechWorld with Nana | 25:10 | 644K |
| [What is Platform Engineering and how it fits into DevOps and Cloud world](https://www.youtube.com/watch?v=ghzsBm8vOms) | TechWorld with Nana | 42:41 | 268K |
| [AWS AI Practitioner Question of the Day \| Question 6 of 65](https://www.youtube.com/shorts/5-yNcSKFyIM) | KodeKloud | Short | 216K |
| [AWS EKS Tutorial \| What is EKS? \| EKS Explained \| KodeKloud](https://www.youtube.com/watch?v=CukYk43agA4) | KodeKloud | 22:28 | 167K |
| [AWS Lambda explained in 60 seconds](https://www.youtube.com/shorts/dlTX_TBpVUs) | KodeKloud | Short | 44K |
| [AWS Certified AI Practitioner (AIF-C01) Exam Questions 2026 \| 40 Mock Questions With Explanations](https://www.youtube.com/watch?v=YGYr-zMIwdw) | KodeKloud | 1:07:28 | 32K |
| [AWS Certified AI Practitioner (AIF-C01): Don’t Take the Exam Before Watching This!](https://www.youtube.com/watch?v=cnqarm7b_hw) | KodeKloud | 23:36 | 5K |

### MLOps

**On the site today:** 0 keyword hits in 0 of the 16 Parts, and 18 roadmap lessons mention it. **Suggested addition:** Pipelines, registries, feature stores and drift. It explains how LLMOps (Part 9) differs from classic MLOps.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [End To End Machine Learning Project Implementation With Dockers,Github Actions And Deployment](https://www.youtube.com/watch?v=MJ1vWb1rGwM) | Krish Naik | 2:44:56 | 523K |
| [End To End Machine Learning Project Implementation Using AWS Sagemaker](https://www.youtube.com/watch?v=Le-A72NjaWs) | Krish Naik | 40:25 | 316K |
| [End To End Deep Learning Project Using MLOPS DVC Pipeline With Deployments Azure And AWS- Krish Naik](https://www.youtube.com/watch?v=p1bfK8ZJgkE) | Krish Naik | 3:51:00 | 274K |
| [MLOps Explained - What It Is, Why You Need It and How It Works](https://www.youtube.com/watch?v=biqYkVf-a7Y) | TechWorld with Nana | 26:23 | 174K |
| [What is MLOps?](https://www.youtube.com/shorts/EwZcKZ_k6d0) | KodeKloud | Short, 2:34 | 35K |
| [MLOps roadmap for 2026!](https://www.youtube.com/shorts/zfkwEoP0WQo) | KodeKloud | Short | 26K |
| [What is Kubeflow?](https://www.youtube.com/shorts/8JT6DS8yt0s) | KodeKloud | Short, 2:53 | 20K |
| [Complete Guide to MLOps \| Machine Learning Essentials](https://www.youtube.com/watch?v=7Xjrp9j9bLw) | KodeKloud | 41:09 | 16K |
| [Kubeflow Explained for Beginners](https://www.youtube.com/watch?v=hvzEPlRdJ2Q) | KodeKloud | 10:40 | 14K |
| [What is MLOps?](https://www.youtube.com/watch?v=QkaDZg-2oM4) | KodeKloud | 12:31 | 11K |
| [6 MLOps skills that separate amateur ML engineers from pros](https://www.youtube.com/shorts/-pnpKGGyUsI) | KodeKloud | Short | 11K |
| [DevOps vs MLOps: Key Differences You MUST Know!](https://www.youtube.com/watch?v=PjPxY-12fHc) | KodeKloud | 7:12 | 9K |
| [How MLOps Works \| Complete Architecture & Workflow Explained](https://www.youtube.com/watch?v=IN3zEeVte8c) | KodeKloud | 5:29 | 7K |

### Metrics, logs and the observability stack

**On the site today:** 5 keyword hits in 2 of the 16 Parts, and 45 roadmap lessons mention it. **Suggested addition:** Prometheus, Grafana, Loki and OpenTelemetry underneath LLM tracing.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [How Prometheus Monitoring works \| Prometheus Architecture explained](https://www.youtube.com/watch?v=h4Sl21AKiDg) | TechWorld with Nana | 21:31 | 1.2M |
| [Setup Prometheus Monitoring on Kubernetes using Helm and Prometheus Operator \| Part 1](https://www.youtube.com/watch?v=QoDqxm7ybLc) | TechWorld with Nana | 25:42 | 509K |
| [Kubernetes Monitoring Made Easy with Prometheus \| KodeKloud](https://www.youtube.com/watch?v=6xmWr7p5TE0) | KodeKloud | 1:08:55 | 101K |
| [How Prometheus Monitoring Works \| Explaining Prometheus Architecture \| KodeKloud](https://www.youtube.com/watch?v=f4W_eEJC-20) | KodeKloud | 13:15 | 42K |
| [Mastering Grafana Loki: Kubernetes Log Collection & Integration \| Part 2](https://www.youtube.com/watch?v=O52dseg2bJo) | KodeKloud | 25:01 | 40K |
| [Best Observability Tools Ranked (2026)](https://www.youtube.com/shorts/tQFCUXTkcLs) | KodeKloud | Short, 2:48 | 25K |
| [What is Grafana Loki?](https://www.youtube.com/shorts/UmJ1vFfGUWg) | KodeKloud | Short | 23K |
| [How Distributed Tracing Works Across Microservices in Kubernetes](https://www.youtube.com/shorts/nzg8KxL5ftI) | KodeKloud | Short | 12K |
| [Prometheus Tutorial for Beginners \| Learn How To Install and Configure Prometheus \| KodeKloud](https://www.youtube.com/watch?v=cl9JlW0nzzE) | KodeKloud | 18:03 | 11K |

### Linux and the shell

**On the site today:** 1 keyword hits in 1 of the 16 Parts, and 128 roadmap lessons mention it. **Suggested addition:** The shell, processes, permissions and networking commands used when running models and agents.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [20% of Linux Commands You'll Use 80% of the Time (Real-World Example)](https://www.youtube.com/watch?v=CLh2ACdXNbc) | TechWorld with Nana | 25:02 | 661K |
| [Bash Scripting Tutorial for Beginners](https://www.youtube.com/watch?v=PNhq_4d-5ek) | TechWorld with Nana | 1:05:33 | 346K |
| [Linux Explained: What Is Linux and Why It’s So Popular in Tech?](https://www.youtube.com/shorts/KyOA2iUXAIM) | KodeKloud | Short | 188K |
| [Linux Crash Course for Beginners \| Free Linux Lab Access \| KodeKloud](https://www.youtube.com/watch?v=a3ujwK65dgs) | KodeKloud | 2:21:13 | 116K |
| [DNS in Linux for the Absolute Beginners!](https://www.youtube.com/watch?v=9nCIjLlLVzY) | KodeKloud | 14:26 | 101K |
| [Linux Tutorial for Beginners [New Step-by-Step Tutorial with FREE LAB ACCESS]](https://www.youtube.com/watch?v=t3e_CaC4V_k) | KodeKloud | 2:20:39 | 76K |
| [3 Bash Tricks Every Developer MUST Know!](https://www.youtube.com/shorts/Tbp3hGHCdzA) | KodeKloud | Short | 43K |
| [Linux Command Every Engineer Should Use!](https://www.youtube.com/shorts/Kkdd7rPEbFA) | KodeKloud | Short | 40K |

### Git and GitHub

**On the site today:** 43 keyword hits in 6 of the 16 Parts, and 194 roadmap lessons mention it. **Suggested addition:** Branching, pull requests and Actions, and versioning prompts and datasets the same way as code.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Why Git Wasn’t Enough for Anthropic!](https://www.youtube.com/shorts/7atGIcL-vRY) | KodeKloud | Short, 2:52 | 389K |
| [Learn Git Worktrees in Under 3 Minutes](https://www.youtube.com/shorts/efVKPUr9D1A) | KodeKloud | Short | 87K |
| [What is Git? \| GIT Basics for DevOps Beginners \| KodeKloud](https://www.youtube.com/watch?v=Lr7sYCrhxE0) | KodeKloud | 17:32 | 58K |
| [Git Introduction for Beginners!](https://www.youtube.com/watch?v=81Uo3C-U_DY) | KodeKloud | 5:04 | 14K |

### Networking fundamentals

**On the site today:** 5 keyword hits in 2 of the 16 Parts, and 29 roadmap lessons mention it. **Suggested addition:** DNS, TLS, proxies and load balancers: the path of one LLM API request.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Proxy vs Reverse Proxy vs Load Balancer \| Simply Explained](https://www.youtube.com/watch?v=xo5V9g9joFs) | TechWorld with Nana | 13:19 | 754K |
| [Every Networking Concept Explained In 20 Minutes](https://www.youtube.com/watch?v=xj_GjnD4uyI) | TechWorld with Nana | 23:21 | 747K |
| [NGINX Explained - What is Nginx](https://www.youtube.com/watch?v=iInUBOVeBCc) | TechWorld with Nana | 14:32 | 701K |
| [Interview: How TCP, TLS and HTTP Actually Work Together](https://www.youtube.com/shorts/lVWXZb_4tU8) | KodeKloud | Short | 344K |
| [Interview: How DNS Finds a Website’s IP Address](https://www.youtube.com/shorts/wEjgtknhLUQ) | KodeKloud | Short | 160K |
| [Network Namespaces Basics Explained in 15 Minutes](https://www.youtube.com/watch?v=j_UUnlVC2Ss) | KodeKloud | 15:32 | 136K |
| [System Design: Designing Load Balancer](https://www.youtube.com/shorts/BpGljU1miLI) | KodeKloud | Short | 131K |
| [The OSI Model: 7 Layers Explained with HTTP Request](https://www.youtube.com/shorts/xuan1dN9bKw) | KodeKloud | Short | 119K |
| [Container Network Interface (CNI) Explained in 7 Minutes](https://www.youtube.com/watch?v=l2BS_kuQxBA) | KodeKloud | 6:23 | 87K |

### DevSecOps and platform security

**On the site today:** 0 keyword hits in 0 of the 16 Parts, and 16 roadmap lessons mention it. **Suggested addition:** Secrets, IAM, supply-chain, container and cluster security around AI workloads.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [What is DevSecOps? DevSecOps explained in 8 Mins](https://www.youtube.com/watch?v=nrhxNNH5lt0) | TechWorld with Nana | 8:20 | 311K |
| [DevSecOps Tutorial for Beginners \| CI Pipeline with GitHub Actions and Docker Scout](https://www.youtube.com/watch?v=gLJdrXPn0ns) | TechWorld with Nana | 1:20:00 | 266K |
| [Kubernetes Security Best Practices you need to know \| THE Guide for securing your K8s cluster!](https://www.youtube.com/watch?v=oBf5lrmquYI) | TechWorld with Nana | 29:41 | 257K |
| [HashiCorp Vault Tutorial for Beginners - What, Why and How](https://www.youtube.com/watch?v=klyAhaklGNU) | TechWorld with Nana | 29:10 | 180K |
| [Shift Left Explained with SQL Injection Bug](https://www.youtube.com/shorts/JctUTCb0oEQ) | KodeKloud | Short | 140K |
| [Secret Store CSI Driver Tutorial \| Kubernetes Secrets \| AWS Secrets Manager \| KodeKloud](https://www.youtube.com/watch?v=MTnQW9MxnRI) | KodeKloud | 31:01 | 113K |
| [Zero Trust Explained in 5 Minutes](https://www.youtube.com/watch?v=q2phcnesXvY) | KodeKloud | 5:56 | 35K |
| [Stop Storing Kubernetes Secrets Like This!](https://www.youtube.com/shorts/JBstJnxbozc) | KodeKloud | Short | 33K |
| [HashiCorp Vault + Terraform: The Ultimate Secrets Management Guide](https://www.youtube.com/watch?v=FQE_gyEwu0Q) | KodeKloud | 18:45 | 18K |
| [AWS IAM Explained in 60 Seconds](https://www.youtube.com/shorts/4TwmceijWM0) | KodeKloud | Short | 17K |

### System design and data infrastructure

**On the site today:** 66 keyword hits in 10 of the 16 Parts, and 100 roadmap lessons mention it. **Suggested addition:** Queues, caches, databases and scaling patterns around an AI application.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Kafka Tutorial for Beginners \| Everything you need to get started](https://www.youtube.com/watch?v=QkdkLdMBuL0) | TechWorld with Nana | 18:33 | 1.5M |
| [Microservices explained - the What, Why and How?](https://www.youtube.com/watch?v=rv4LlmLmVWk) | TechWorld with Nana | 18:30 | 1.1M |
| [Istio & Service Mesh - simply explained in 15 mins](https://www.youtube.com/watch?v=16fgzklcF7Y) | TechWorld with Nana | 16:09 | 828K |
| [System Design for Beginners (2026)](https://www.youtube.com/watch?v=SE2KF-vxvS0) | KodeKloud | 1:25:37 | 768K |
| [Redis Crash Course - the What, Why and How to use Redis as your primary database](https://www.youtube.com/watch?v=OqCK95AS-YE) | TechWorld with Nana | 23:37 | 589K |
| [System Design: Notifying 50 Million Users in One Shot](https://www.youtube.com/shorts/uZDNJq18YL0) | KodeKloud | Short | 267K |
| [Consistent Hashing Explained (System Design Basics)](https://www.youtube.com/shorts/AIuZExZFHNU) | KodeKloud | Short | 255K |
| [Postgres Hit the Connection Limit. Now What?](https://www.youtube.com/shorts/-C_EKxhwYew) | KodeKloud | Short | 219K |
| [Change Data Capture (CDC) Explained for Beginners](https://www.youtube.com/watch?v=K83NPFfWPBw) | KodeKloud | 9:54 | 84K |
| [Apache Kafka Crash Course \| Kafka Tutorial for Beginners \| KodeKloud](https://www.youtube.com/watch?v=cNFAP9OnJjo) | KodeKloud | 1:02:12 | 47K |
| [Database Sharding Explained for Beginners (with Hands-On Labs)](https://www.youtube.com/watch?v=WpXmMxIgzdU) | KodeKloud | 48:54 | 44K |

### AIOps (AI for IT operations)

**On the site today:** 1 keyword hits in 1 of the 16 Parts, and 14 roadmap lessons mention it. **Suggested addition:** Using LLMs for incident response, anomaly detection and runbooks.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [ChatGPT Tutorial - Use ChatGPT for DevOps tasks to 10x Your Productivity](https://www.youtube.com/watch?v=l-kE11fhfaQ) | TechWorld with Nana | 1:07:43 | 681K |
| [GitHub Copilot Tutorial \| How useful is it for Cloud and DevOps?](https://www.youtube.com/watch?v=9JGONx_X4ho) | TechWorld with Nana | 43:43 | 191K |
| [What is AIOps and how does it differ from DevOps and MLOps?](https://www.youtube.com/shorts/uKQQzrq9Cqw) | KodeKloud | Short | 23K |
| [The complete AIOps roadmap you need to know!](https://www.youtube.com/shorts/lmY94ldWa3Q) | KodeKloud | Short | 22K |
| [What is AIOps? How It Differs from DevOps and MLOps](https://www.youtube.com/watch?v=_cexdeRAtCg) | KodeKloud | 3:44 | 14K |
| [Every DevOps Engineer Should Know AIOps [FREE LABs]](https://www.youtube.com/watch?v=SUAHtdDBeps) | KodeKloud | 12:49 | 8K |

### AI coding assistants

**On the site today:** 33 keyword hits in 6 of the 16 Parts, and 56 roadmap lessons mention it. **Suggested addition:** Claude Code, Cursor, Copilot and Gemini CLI: workflows, context files and MCP servers.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Claude Code Explained in 60 Seconds](https://www.youtube.com/shorts/p7U_98jWqWo) | KodeKloud | Short, 1:18 | 665K |
| [Complete Claude Code Course In 2 Hours For Developers](https://www.youtube.com/watch?v=TAKDIvvUdc4) | Krish Naik | 1:58:35 | 323K |
| [How I reduced 90% errors for my Cursor (+ any other AI IDE)](https://www.youtube.com/watch?v=1L509JK8p1I) | AI Jason | 15:30 | 289K |
| [I spent 400+ hours in Cursor, here’s what I learned](https://www.youtube.com/watch?v=gYLNxUxVomY) | David Ondrej | 46:40 | 187K |
| [A Complete Guide to Claude Code - Here are ALL the Best Strategies](https://www.youtube.com/watch?v=amEUIuBKwvg) | Cole Medin | 50:17 | 151K |
| [I was using Claude Code wrong... The Ultimate Workflow](https://www.youtube.com/watch?v=UZb0if-7wGE) | AI Jason | 18:44 | 142K |
| [Gemini CLI: Open-Source AI in Your Terminal](https://www.youtube.com/shorts/mDAnW8MUVlQ) | KodeKloud | Short | 51K |
| [Claude Code Explained for Beginners](https://www.youtube.com/watch?v=sxp-VXbXZU4) | KodeKloud | 9:01 | 41K |
| [Claude Code Tutorial For Beginners](https://www.youtube.com/watch?v=3nnw06bY4mM) | KodeKloud | 2:48:40 | 23K |
| [GitHub Copilot Crash Course: Ultimate Guide for Developers](https://www.youtube.com/watch?v=yFzMwsuAkr8) | KodeKloud | 38:31 | 17K |
| [Gemini CLI: The Open Source Tool for AI Development](https://www.youtube.com/watch?v=gycx9tnmyPM) | KodeKloud | 9:50 | 13K |
| [Cursor CLI Tutorial for Beginners](https://www.youtube.com/watch?v=ywz8cNJvM5Y) | KodeKloud | 12:11 | 10K |

### Python and YAML for DevOps/AI work

**On the site today:** 105 keyword hits in 14 of the 16 Parts, and 535 roadmap lessons mention it. **Suggested addition:** Python tooling and YAML/config literacy for the pipeline files above.

| Resource | Channel | Length | Views |
| --- | --- | --- | --- |
| [Python Tutorial for Beginners - Learn Python in 5 Hours [FULL COURSE]](https://www.youtube.com/watch?v=t8pPdKYpowI) | TechWorld with Nana | 5:31:30 | 6.9M |
| [Yaml Tutorial \| Learn YAML in 18 mins](https://www.youtube.com/watch?v=1uFVr15xDGg) | TechWorld with Nana | 18:05 | 772K |
| [Why Is Python Slow Compared to C and C++?](https://www.youtube.com/shorts/gPOaMdNDpto) | KodeKloud | Short | 210K |
| [YAML Explained: A Beginner's Guide in 10 Minutes](https://www.youtube.com/watch?v=o9pT9cWzbnI) | KodeKloud | 8:26 | 137K |
| [Meet UV — The Fastest Python Package Manager](https://www.youtube.com/shorts/PXO9wfRa3SA) | KodeKloud | Short | 28K |

## How the clips were chosen

- On topic for the section it sits in, taken from the section's own text, then read in the transcript: the opening, the ending, and a sample of the middle for long videos.
- Left out: factual errors, hype or news titles, trailers and enrolment pitches, product launches that are already dated, code-alongs tied to a model or library version that has since changed, and clips that repeat another clip.
- At most 5 KodeKloud clips and 4 clips from the other creators per section, at most 3 from one creator, and at most 2 videos over 30 minutes.
- A Short is at most 180 seconds, and `seconds` comes from the player.
- Sponsor segments and community plugs are not a reason to leave a good clip out. The review log notes them.

## Keeping it true

`npm run check:videos` asks YouTube whether every listed video is still public and embeddable, still has its stored title and channel, and whether a Short is still a Short. `npm run check:videos -- --channel "Cole Medin"` checks one channel. Run it by hand: `npm test` and the deploy never touch the network.
