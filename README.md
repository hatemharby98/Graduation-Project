<div align="center">
  <h1>🛡️ DefendX: AI-Driven Intrusion Prevention System (AI-IPS)</h1>
  <p><b>A Fully Integrated Cybersecurity Ecosystem: AI, Networking, Web, and Cloud DevSecOps</b></p>
  
  [![AI](https://img.shields.io/badge/AI-Deep_Learning-ff6f00?logo=tensorflow)](#)
  [![Security](https://img.shields.io/badge/Security-Red/Blue_Team-cc0000?logo=tryhackme)](#)
  [![Web](https://img.shields.io/badge/Web-ASP.NET_Core-512BD4?logo=dotnet)](#)
  [![Network](https://img.shields.io/badge/Network-GNS3_%7C_FortiGate-00B140?logo=cisco)](#)
  [![Cloud](https://img.shields.io/badge/Cloud-AWS_%7C_K8s-232F3E?logo=amazon-aws)](#)
</div>

---

##  Executive Summary

**DefendX** is a comprehensive, enterprise-grade Intrusion Prevention System (IPS) developed as a graduation project at Sohag University. It transcends traditional signature-based security by integrating five core technological domains into a single, cohesive pipeline: **Artificial Intelligence, Cybersecurity, Web Development, Network Architecture, and Cloud/DevOps**. 

By intercepting live traffic, evaluating it through a Multimodal Dual-Head Neural Network, and autonomously enforcing kernel-level packet blocking, DefendX offers real-time defense against zero-day exploits, volumetric floods, and application-layer attacks.

---

##  Enterprise Value & Business Impact

In today’s rapidly evolving threat landscape, traditional signature-based security systems are no longer sufficient. Enterprises face massive financial and reputational risks from unseen exploits and advanced persistent threats (APTs). **DefendX** is engineered to provide immense value to corporate environments:

*   **Proactive Zero-Day Mitigation:** By analyzing behavioral flow patterns and payload semantics instead of static signatures, DefendX stops entirely new, unknown attacks before they compromise critical infrastructure.
*   **Eliminating SOC Alert Fatigue:** Traditional IPS generates overwhelming false positives. DefendX utilizes a 20-flow batch consensus mechanism, ensuring Security Operations Center (SOC) analysts only receive highly accurate, actionable alerts.
*   **Ensuring Business Continuity:** Automated, kernel-level blocking instantly neutralizes disruptive volumetric attacks (like DDoS, HULK, and Slowloris), ensuring enterprise web services, APIs, and databases remain online.
*   **Data Breach Prevention:** Deep inspection of HTTP payloads intercepts application-layer attacks (such as SQL Injection and Cross-Site Scripting) in real-time, safeguarding sensitive corporate and customer data.
*   **Compliance & Audit Readiness:** Comprehensive SQL Server logging and automated PDF reporting streamline compliance audits and provide clear forensic trails after security events.

---

##  The 5 Pillars of DefendX

### 1.  Artificial Intelligence & Deep Learning
The intelligence layer of DefendX is built to understand both the statistical behavior of network flows and the semantic context of web payloads.
*   **Multimodal Architecture:** Processes 80+ numerical flow features (extracted via NFStream) and tokenizes HTTP payloads simultaneously using an Embedding layer.
*   **Dual-Head Prediction:** 
    *   *Anomaly Detection Head:* A binary classifier (Sigmoid) designed to catch unseen/zero-day attacks (Achieved **100% Accuracy**).
    *   *Classification Head:* A multi-class classifier (Softmax) that categorizes threats into 11 distinct families (Achieved **94%-97% F1-Score** on live traffic).
*   **Data Augmentation:** Overcame dataset imbalance using a custom cluster-based bootstrapping technique with statistical perturbation.

### 2.  Cybersecurity (Red & Blue Team Operations)
DefendX implements a proactive Defense-in-Depth strategy, tested rigorously against custom-built attack vectors.
*   **Blue Team (Defense):** Replaces static rules with a 20-flow batch consensus algorithm to eliminate false positives. Malicious IPs are instantaneously blacklisted and blocked at the OS kernel level using **WinDivert**.
*   **Red Team (Attack Simulation):** We engineered a custom Python-based attack suite simulating real-world threats, including Botnets, Multi-port LOIC DDoS, SlowHTTPTest, GoldenEye, HULK, Advanced Port Scanning, Brute Forcing, Infiltration, and Heartbleed exploits.

### 3.  Web Application & Real-Time Dashboard
A centralized SOC dashboard provides administrators with complete visibility and control over the network's security posture.
*   **ASP.NET Core MVC & Entity Framework Core:** Robust backend architecture for managing users, threat catalogs, and event logs.
*   **Real-Time Telemetry (SignalR):** Sub-second WebSocket communication broadcasts new attack alerts, updates statistics cards, and renders live Chart.js attack distributions without page reloads.
*   **Role-Based Access Control (RBAC):** Strict admin/user hierarchies with email verification and automated PDF report generation (via QuestPDF).

### 4.  Network Architecture & Engineering
The system was validated within a highly realistic, hierarchical enterprise network topology.
*   **Simulated Enterprise Network:** Built using GNS3 and VMware, featuring Core, Distribution, and Access layers.
*   **Network Segmentation:** Complete with VLANs, OSPF routing, and a dedicated DMZ hosting web and FTP services.
*   **FortiGate Integration:** Next-Generation Firewall (NGFW) policies configured for zone-based protection, NAT, and traffic logging.

### 5.  Cloud Infrastructure & DevSecOps
DefendX embraces modern software engineering practices to ensure high availability, scalability, and security during deployment.
*   **Containerization:** The AI Engine (FastAPI) and the Web Dashboard are packaged into optimized, multi-stage Docker containers.
*   **Orchestration & Cloud:** Deployed on **AWS EC2** using a lightweight Kubernetes (**k3s**) cluster, with persistent data stored on AWS RDS (SQL Server).
*   **CI/CD Pipeline:** Fully automated GitHub Actions workflow for building, testing, and deploying. It includes mandatory vulnerability scanning of Docker images using **Trivy**.
*   **Observability:** Continuous infrastructure monitoring and health tracking via **Prometheus** and **Grafana**.

---

##  How It Works (End-to-End Flow)

1.  **Ingestion:** NFStream captures live packets from the network interface and reconstructs bidirectional flows.
2.  **Inference:** The FastAPI AI module standardizes the data and evaluates it through the Dual-Head model in `< 200ms`.
3.  **Consensus:** The ASP.NET backend aggregates 20 events into a batch and applies majority-vote logic to confirm the threat.
4.  **Mitigation:** The desktop IPS service creates a WinDivert rule, dropping all future packets from the attacker's IP.
5.  **Alerting:** SignalR pushes the event to the Web Dashboard, instantly alerting the security administrator.

---

##  The DefendX Team

This project was developed by the graduation project team at the **Telecommunications Engineering Department, Sohag University**.

*   **Team Leader:** Hatem Harby Mohamed
*   **Development Team:** Al Moataz Bellah Mahmoud, Hossam Fathy, Kerolos Nader, Mohamed Khaled, Saleh Ali, Aya Ali, Israa Khalaf, Roaa Ahmed, Sara Atef, Mohamed Hamdy, and Mohamed Ibrahim.
*   **Supervised By:** Assoc. Prof. Dr. Safwat Mohamed Ramzy & Eng. Mohamed Elsagheer.

---

##  Legal Disclaimer
The attack simulation scripts included in the `RedTeam_Tools` directory were developed exclusively for academic research, algorithm training, and authorized penetration testing within an isolated laboratory. The authors are not responsible for any misuse of these tools.
