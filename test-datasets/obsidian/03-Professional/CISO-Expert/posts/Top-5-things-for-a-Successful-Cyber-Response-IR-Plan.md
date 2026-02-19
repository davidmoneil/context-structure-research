---
title: "Top 5 things for a Successful Cyber Response 'IR' Plan"
type: post
status: publish
date: 2022-01-11 18:02:00
source: cisoexpert.com
original_url: https://cisoexpert.com/top-5-successful-incident-response-ir-plan/
imported: 2026-01-30T21:53:08.650069
version: 1
version_history:
  - v1: "2026-02-10 - Backfill versioning (original content)"
---

# Top 5 things for a Successful Cyber Response 'IR' Plan

Incident Response Planning & Strategy

How important is an Incident Response Plan? Some studies show that just having a plan, can reduce the cost of a breach [example one](https://insights.integrity360.com/cost-of-a-data-breach-2021), shows a 43% reduction in the cost of a data breach. I have provided a quick bullet point explanation of the top 5 things for a successful incident response IR plan and a more detailed section with practical examples for your use.  

Why is there such a dramatic decrease in the overall costs of a breach when you have an incident response plan?  

- Everyone knows what they should be doing, so time is more efficently used. 
- If you are quicker to react, you reduce the impact of the overall event. *examples:* reduced number of records exfiltrated 
- less nunmber of systems impacted for remeidation 
- less time spent by third party teams (incident response, legal, breach response, etc. ) 
- Consolidated understanding and agreement by the business on the specific actions the security team is empowered to take to protect the business from potential risks. 

I have put together this list of the 'Top 10 Sections to include in your Incident Response Policy / Plan' based on my experience and research into successful incident response programs.  For instance, this is the same information that I professionally use when reviewing organizations rating their 'Incident Response maturity. 
*No specific order *

- **Terms & Definitions** will build a common language of understanding. 
- **Signature Page **for Executive Buy-in and a Right-To-Act 
- **Roles and Responsibilities** across the organization (with decisions makers) 
- Security **Incident Severity Matrix** based on business impact (a sample 'Threat Model') 
- High Level** IR Workflow **or Swimlane document 

*Additional details below that you can implement today. *

Also, read "Top 5 common blunders in  your Incident Response Policy"

## 1.0 Terms & Definitions

Outlining terms will be important when it comes to critical aspects that impact the rest of the business.  Such terms include some of the following:  

- Event Data = described as an event as 'any observable occurrence in a system or network' and examples include data that describes user authentications, system logging events, request to a service, the response of those requests, utilization of tools and technologies, tracking data, firewall blocks and allows, packet data, and other data sources. 

*Often referenced as contextual data that supports and is referenced by a Security Incident. 
*
- Security Event = is a set of event or events that have the potential to impact the business. Until investigated, a security event does not have an incident severity or classification.   

- Security Incident = 'is a violation of or imminent threat of violation or cumpter security policies, acceptable use policies, or standard security practices'. 

- Breach = is a business impacting security incident 
- Crisis = 
- Contractual Obligation =  
- SIEM = Security Information Event Management 

Terms and definitions referenced from the NIST standards [NIST SP 800 ](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf)

## 2.0 Signature Page with Right-to-Act 

Why have a signature page?  The Signature is an area for security to get executive buy-in to the program specifics.  It also acts as a 'pre-authorization' on actions the cyber security team can and will take (without change order or business leader buy-in) during critical incidents to protect the business from additional risks.  

In the past, I have added to an IR plan, where organizations struggle to get around long-established processes, such as a rigorous change order process, a 'Right to Act' clause.  That clearly outlines the type of activities a security organization can and should be empowered to make in critical incidents (see 4.0 around Incident Severity).  

## 3.0 Roles and Responsibilities 

Ok, so this one seems straight forward and you most likely already have this within your own plan.  Consider the following bullet points. As I often see teams make the following mistakes within their IR policy

- The IR plan have a list of specific individuals, and their responsibilities is based on their primary job function Roles should be based on function needed wihtin the IR process, allowing for anyone to step in and preform that function.  This builds resiliency into your IR plan by ensuring you aren't locked into specific roles and responsibilities. 
- The 'roles' are only focused on the security team. Roles should include the IT team, Executive team, and third party support teams.  I like to provide the following high level breakdown into the appropirate teams **CORE **= This is the team that will be running the show and doing the majority of the technical work.  It can include security analysts, CISO, and IT leadership.  
- **Extended **= This will be members that are needed for decision and awareness, but don't play a role in the overall incident.  Examples are legal, people resources  (HR), business unit owners, & third-party supporting teams.   
- **Executive **= This is the group that makes the business impacting decisions.  This includes the C-Suite and any other business leader that will have their business impacted in a negaitive way due the the security incident. 
- In section 4.0 (the next one) I will discuss Incident Severity, which will plan a role into when you activate each of these teams.  Note that a one size fits all approach, is only good if your Incident Response plan is focused on the critical incidents and not all security events. 

## 4.0 Incident Severity Matrix 

A lot of organizations struggle with this idea for multiple reasons. 

- They are trying to limit confusion so othey have only a single 'security incident' status If you are currently taking this approach, it is most likely confusing to your organization.  If everything is a security incident, when does the extended team know to prioritize their work vs the security incident work? 
- Creating clear expetations around a Low, Medium, High, & Critical will be important to determining the apporpirate level of response. 
- They attempt to adopt the IT severity standard instead of having their ownWhen you map your security incident to the same SLA as IT, you are sending out mixed messages.  I have seen where some IT standard response is (level 3 or 4) and has an SLA of 8 hours (out sourced IT can be even more impactful on SLA response).  If you are blocking an IP address and need to stop the potential spread of a (domain based link) in a phishing email, you need to do that ASAP.  

I wouldn't expect that you would want to raise a critical IT ticket, which could have its own set of escalations and notifications just to block / blacklist a domain.  The solution is that you defined specific actions within each severity that should have a specific SLA attached to them.  This will become more important as you develop your metrics program.  Being able to define your escalation process into IT and the number of incidents that are 'business impacting' and to what degree will be critical.  
- Or they don't mapp their incident severity against any severities within the organization (IT, BCP, or Crisis)The mapping is intended to be a straight forward understanding of the way in which all incident types are considered by the business. See example below 

Info-Tech (IT)Security BCPDR Critical   Critical   Critical   Critical  Critical  Critical  Critical High Critical  CriticalHighMediumCriticalCriticalMediumLowHighHighLowNAMediumMediumNANALowMediumNANANALowNANAIncident Severity Mapping Example

- They don't take into account the potential for business impact when picking the event severity (which should trigger 3.0 Roles and Responsibilities). 
- The Incident Severity Matrix is based on only a single type of incident severity and not specific to the potential business impact or potential impact it could cause.  Ex: If your incident severity is based on the number of assets and you are looking at phihsing vs ransomware incidents.  It should be obeuse that these events have different levels of business impacts.  
- Coming Soon - Ways to classify Incident Response Severity with busines impacts. (link) 

## 5.0 IR Workflow 

Having a high-level incident response workflow will help your organization and team understand their roles and visualize potential breakdowns in that process.  Utilizing a Swimlane diagram is a fundamental way to provide a quick high-level view of how the incident response process will engage teams throughout the business. 

Build your swimlane workflow with a focus on the high-level roles discussed in section 3.0 of this document. When socializing this document with your extended and c-suite teams, it is clear that their involvement is dependent on the incident severity, and impact on the business units established within the workflow diagram.   

However, you choose to implement your incident response strategy, ensure that you have considered the larger impact that the IR plan has on your business.  Furthermore, aligning your incident response strategy to the actual implementation of your IR plan will provide you with the best opportunity for a reduction in your cyber risk.  

Additionally, there has been an increase in 2021 around the number of cyber-insurance providers asking to see a copy of the incident response process to gauge your organizational maturity around cyber security.