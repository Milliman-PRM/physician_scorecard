/*
### CODE OWNERS: Kelsie Stevenson, Ben Copeland

### OBJECTIVE:
  Write a trigger to inform the QVW publisher of the appropriate sqlite
  database and QVW template

### DEVELOPER NOTES:
  Builds on top of the same datamart as the CCR currently
*/
%include "%sysget(INDYHEALTH_LIBRARY_HOME)\include_sas_macros.sas" / source2;
options compress = yes;
%include "%sysget(ANALYTICS_PIPELINE_HOME)\010_Master\Supp01_Parser.sas" / source2;
%include "&M002_cde.Supp01_Validation_Functions.sas";
%include "&M013_cde.Supp02_Export_Wrappers.sas";

/* Libnames */

/**** LIBRARIES, LOCATIONS, LITERALS, ETC. GO ABOVE HERE ****/

/*In postboarding world, temporary locations may not exist. Write_Trigger relies on custom
   SAS functions that try to compile to m008_tmp. Make sure this location is accessible.*/
%macro ensure_tmp();
	%if not(%isdir(&m008_tmp.)) %then %do;
		%let m008_tmp = %mockdirectorygetpath();
		%createfolder(&m008_tmp.)
	%end;
%mend ensure_tmp;
%ensure_tmp()

%macro trigger_wrapper();
	%if %isdir(%sysget(Physician_Scorecard_Home)\.git) %then %do;
		*Use the .qvw template from develop if we are running from source control.;
		%let path_dir_template_coalesce = %sysget(PHYSICIAN_SCORECARD_GIT_QVW_PATH)\Reporting\_Compiled_QVWs\;
	%end;
	%else %do;
		*Otherwise, use the template of the specified release;
		%let path_dir_template_coalesce = %sysget(PHYSICIAN_SCORECARD_HOME)\Reporting\_Compiled_QVWs\;
	%end;

	/*Write the trigger.*/
	%Write_Trigger(
		Physician_Scorecard
		,PS
		,%str(&client_id.01)
		,TBD.sqlite
		,True
		,&path_dir_template_coalesce.
		)
%mend;

%trigger_wrapper();

%put System Return Code = &syscc.;
