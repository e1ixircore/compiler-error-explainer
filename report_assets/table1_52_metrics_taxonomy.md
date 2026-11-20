# Table 1: 52-Metric Security Taxonomy

| Metric ID | Metric Name | Category | CWE | Severity | Weight | Kind |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `SEC_01` | OS Command Injection | Injection & Execution | `CWE-78` | **CRITICAL** | 10.0 | detector |
| `SEC_02` | Dynamic Code Evaluation | Injection & Execution | `CWE-95` | **CRITICAL** | 9.5 | detector |
| `SEC_03` | Insecure Deserialization | Injection & Execution | `CWE-502` | **CRITICAL** | 9.0 | detector |
| `SEC_04` | Raw SQL Injection | Injection & Execution | `CWE-89` | **CRITICAL** | 9.0 | detector |
| `SEC_05` | XML External Entity (XXE) | Injection & Execution | `CWE-611` | **HIGH** | 7.0 | detector |
| `SEC_06` | Server-Side Template Injection | Injection & Execution | `CWE-1336` | **HIGH** | 7.5 | detector |
| `SEC_07` | LDAP / XPath Injection | Injection & Execution | `CWE-90` | **HIGH** | 7.0 | detector |
| `SEC_08` | Unsafe Dynamic Import | Injection & Execution | `CWE-470` | **HIGH** | 7.0 | detector |
| `SEC_09` | MRO Class Traversal | Sandbox Escape & Reflection | `CWE-269` | **CRITICAL** | 9.0 | detector |
| `SEC_10` | Builtins Namespace Poisoning | Sandbox Escape & Reflection | `CWE-668` | **CRITICAL** | 9.0 | detector |
| `SEC_11` | Frame Inspection / Stack Walking | Sandbox Escape & Reflection | `CWE-489` | **HIGH** | 7.5 | detector |
| `SEC_12` | Native Code Binding | Sandbox Escape & Reflection | `CWE-111` | **HIGH** | 8.0 | detector |
| `SEC_13` | Global Symbol Table Tampering | Sandbox Escape & Reflection | `CWE-471` | **MEDIUM** | 5.0 | detector |
| `SEC_14` | Reflection Obfuscation | Sandbox Escape & Reflection | `CWE-912` | **HIGH** | 7.5 | detector |
| `SEC_15` | Directory / Path Traversal | File System & Path Traversal | `CWE-22` | **HIGH** | 7.5 | detector |
| `SEC_16` | Destructive File Operations | File System & Path Traversal | `CWE-73` | **HIGH** | 8.0 | detector |
| `SEC_17` | Insecure Temporary File | File System & Path Traversal | `CWE-377` | **MEDIUM** | 5.0 | detector |
| `SEC_18` | Sensitive System Path Access | File System & Path Traversal | `CWE-552` | **HIGH** | 7.0 | detector |
| `SEC_19` | Overly Permissive File Permissions | File System & Path Traversal | `CWE-732` | **MEDIUM** | 5.5 | detector |
| `SEC_20` | Symlink / Arbitrary File Write | File System & Path Traversal | `CWE-59` | **MEDIUM** | 4.5 | detector |
| `SEC_21` | Hardcoded Credentials / High-Entropy Secrets | Cryptography & Secrets | `CWE-798` | **HIGH** | 7.5 | detector |
| `SEC_22` | Weak Pseudo-Random Generator | Cryptography & Secrets | `CWE-338` | **MEDIUM** | 4.0 | detector |
| `SEC_23` | Deprecated Hash Algorithm (MD5/SHA1) | Cryptography & Secrets | `CWE-328` | **MEDIUM** | 5.0 | detector |
| `SEC_24` | Weak Symmetric Cipher (DES/RC4/ECB) | Cryptography & Secrets | `CWE-327` | **HIGH** | 6.5 | detector |
| `SEC_25` | Static IV / Hardcoded Salt | Cryptography & Secrets | `CWE-329` | **MEDIUM** | 5.5 | detector |
| `SEC_26` | Disabled TLS Certificate Verification | Cryptography & Secrets | `CWE-295` | **HIGH** | 7.5 | detector |
| `SEC_27` | Weak Key Size / Insecure SSL Version | Cryptography & Secrets | `CWE-326` | **HIGH** | 6.5 | detector |
| `SEC_28` | Server-Side Request Forgery (SSRF) | Network & Server-Side Security | `CWE-918` | **HIGH** | 7.5 | detector |
| `SEC_29` | Unrestricted Socket Binding | Network & Server-Side Security | `CWE-1327` | **MEDIUM** | 5.0 | detector |
| `SEC_30` | Sensitive Data Exposure in Logs | Network & Server-Side Security | `CWE-532` | **LOW** | 3.0 | detector |
| `SEC_31` | Cleartext Protocol Usage | Network & Server-Side Security | `CWE-319` | **MEDIUM** | 5.0 | detector |
| `SEC_32` | HTTP Header / CRLF Injection | Network & Server-Side Security | `CWE-113` | **MEDIUM** | 5.5 | detector |
| `SEC_33` | Debug Mode / Open Redirect Exposure | Network & Server-Side Security | `CWE-601` | **MEDIUM** | 5.0 | detector |
| `SEC_34` | Regular Expression DoS (ReDoS) | DoS & Resource Control | `CWE-1333` | **MEDIUM** | 5.5 | detector |
| `SEC_35` | Unbounded File / Stream Read | DoS & Resource Control | `CWE-400` | **LOW** | 2.5 | detector |
| `SEC_36` | Unbounded Loop Hazard | DoS & Resource Control | `CWE-835` | **MEDIUM** | 4.5 | detector |
| `SEC_37` | Unbounded Recursion Hazard | DoS & Resource Control | `CWE-674` | **MEDIUM** | 4.5 | detector |
| `SEC_38` | Archive / Decompression Bomb | DoS & Resource Control | `CWE-409` | **HIGH** | 6.5 | detector |
| `SEC_39` | Subprocess / Request Missing Timeout | DoS & Resource Control | `CWE-400` | **LOW** | 3.0 | detector |
| `SEC_40` | Unbounded Thread / Process Spawning | DoS & Resource Control | `CWE-410` | **MEDIUM** | 4.5 | detector |
| `SEC_41` | Buffer Overflow / Unsafe C String | Low-Level & Memory Safety | `CWE-120` | **CRITICAL** | 9.0 | detector |
| `SEC_42` | Use-After-Free / Raw Pointer Risk | Low-Level & Memory Safety | `CWE-416` | **HIGH** | 8.0 | detector |
| `SEC_43` | Double Free Hazard | Low-Level & Memory Safety | `CWE-415` | **HIGH** | 8.0 | detector |
| `SEC_44` | Format String Vulnerability | Low-Level & Memory Safety | `CWE-134` | **HIGH** | 7.0 | detector |
| `SEC_45` | Unchecked Allocation / Bare Assert-Except | Low-Level & Memory Safety | `CWE-252` | **LOW** | 3.0 | detector |
| `SEC_46` | Taint Flow Count | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
| `SEC_47` | Dangerous Sink Density (%) | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
| `SEC_48` | Security Cyclomatic Density | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
| `SEC_49` | Unsanitized Parameter Index | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
| `SEC_50` | Privilege Exposure Score | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
| `SEC_51` | Peak String Secret Entropy | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
| `SEC_52` | Overall Security Health Score | Quantitative Attack Surface | `METRIC` | **INFO** | 0.0 | quantitative |
