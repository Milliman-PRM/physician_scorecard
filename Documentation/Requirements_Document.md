# Requirements Document

## Introduction
Our clients are looking for a way to easily look up their providers and see how they are doing relative to one another, specifically in terms of quality measures. They want to be able to easily pull up a provider and see a list of the providers members and take action on the members that need it.

### Purpose
The purpose of this dashboard/scorecard is to allow a physicians manager to quickly and easily see how their providers are doing with respect to quality measures. We would like the manager to be able to choose specific providers and be able to export a list of that providers members to take action on.

### Background
The reasoning behind developing this dashboard is that clients have been asking for a way to easily figure out how their providers are doing with respect to quality measures. 

### References
Interviewed consultants within the PRM office to see what their clients were asking for.

### Assumptions
 * Milliman PRM Analytics will provide hosting for the tool
 * The tool will follow this data schema:
 *image here*
 * Quality measure targets are accurate to the clients goals

### Constraints
Quality measures will differ for each client. There isn't an easy way to display the various types of quality measures.

### Acronyms & Terms
 * **DOB** - Date of Birth
 * **ER** - Emergency Room
 * **IP** - Inpatient
 * **NPI** - National Provider Identifier
 * **OP** - Outpatient
 * **PMPM** - Per Member per Month
 * **QMs** - Quality measures
 * **SNF** - Skilled Nursing Facility 
 * **TIN** - Taxpayer Identification Numbers

### Roles & Responsibilities
Name | Contact Information | Role | Responsibilites
:---| :---| :--- | :---
Michael Reisz | michael.reisz@milliman.com | Development Coordinator | Coordinate UI development, Provide initial UI mockup, Define data model
Kelsie Stevenson | kelsie.stevenson@milliman.com | Developer | Work on initial UI mockup, Help define data model

## Requirements
This project requires...

### User Requirements
User must be able to 
 * See all of the providers
 * Search for provider by
	 * Provider name
	 * TIN
	 * NPI
 * Select a single provider
 * See utilization/1000 for a single provider
	 * ER
	 * IP
	 * SNF
	 * Home health
	 * Hospice
	 * Office
	 * Pharmacy
 * See PMPM for a single provider
 * See risk scores for a single provider
 * See quality measures at the population level
 * See quality measures at the provider level
 * See quality measures at the member level
 * See a comprehensive list of all members assigned to a specific provider
 * Print/send to excel
	 * Provider list
	 * Quality measures
	 * Member list

### Functional Requirements
This report needs to be updated monthly

### Architecture/Design Requirements
 * Ability to see quality measures from population level to provider level to member level
 * Compare quality measures to the target

### Performance Requirements

### Security Requirements
The report needs to be reducable.

### Other Requirements
None.

### Project Lifecycle/Update Requirements
 * Lifecycle - monthly updates.
 * Update as needed with version releases.
 * 