# BOTNET ATTACK DETECTION

## PROBLEM STATEMENT

Detecting a BotNet Attack on the NF-BoT-IoT dataset. Following the detection phase, we attempted to classify the attack as DOS, DDOS, Reconnaisance or Theft. The advantage of this problem statement lies in its comprehensive approach to network security. By first detecting BotNet attacks on the NF-BoT-IoT dataset, you establish a foundational layer of defense against malicious activities. Subsequently, classifying the attack into specific types such as DOS, DDOS, Reconnaissance, or Theft allows for a more fine-grained understanding of the threat landscape. This detailed classification empowers network administrators and security professionals to tailor their response strategies more effectively. For example, they can allocate resources to mitigate the specific type of attack, implement targeted countermeasures, and prioritize incident response efforts. In essence, this approach enhances the network's resilience and security posture by providing actionable insights that help proactively safeguard against a wide range of potential threats.

## OBJECTIVE 

Detecting a BotNet Attack on the NF-BoT-IoT dataset. Following the detection phase, we attempted to classify the attack as DOS, DDOS, Reconnaisance or Theft. 

## DATASET

The NF-BoT-IoT dataset contains 4,80,080 entries in the training dataset and 1,20,020 entries in the test dataset. It comprises of the following features - 'IPV4_SRC_ADDR', 'L4_SRC_PORT', 'IPV4_DST_ADDR','L4_DST_PORT', 'PROTOCOL', 'L7_PROTO', 'IN_BYTES', 'OUT_BYTES','IN_PKTS', 'OUT_PKTS', 'TCP_FLAGS', 'FLOW_DURATION_MILLISECONDS', 'Label' and 'Attack'

## RESULTS

The results of the Attack classification model are as shown below - 

#### Classes

<img width="362" alt="image" src="https://github.com/manya0702/BotNet-Attack-Detection/assets/72210577/87d703d2-acd9-4e7e-a280-78f57761891d">

#### Classification Report

<img width="285" alt="image" src="https://github.com/manya0702/BotNet-Attack-Detection/assets/72210577/18fd88c8-f63a-47a8-94f9-eb723abb5acb">


#### Confusion Matrix

<img width="154" alt="image" src="https://github.com/manya0702/BotNet-Attack-Detection/assets/72210577/318e6b8a-28c6-4376-8782-49ce2f198eeb">
