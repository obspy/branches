#include <ctype.h>
#include <time.h>
#include <string.h>
#include <memory.h>
#include <malloc.h>
#include <math.h>
#include "nr.h"
#include "nrutil.h"
#include "xcorr_detect.h"

/*
Synopsis:
	Performs a cluster analysis of waveforms from different seismic events
	based on waveform correlation. Input is a phase pick file; Output is 
	a matrix containing the correlation coeffitents
*/

main()
{

/* database stuff */
    DB_ADDR		dba,dba2;
    Trace_rec		trace_rec_a;
    Station		station;
    Calibration tmp_cal;                /* temporary calibration record */
    Calibration check_cal;              /* calibration record check */
    Calibration calib;                 /* calibration record list */
/*---------------*/
    
/* Time specifcations */
    TIME		onset_t;
    TIME		delta_st;
    TIME		input1,input2;
    struct tm		gsetime;
    double		delta_ed;
    double		start_sel,end_sel;
    double              start_time_old;
/*--------------------*/

/* input output files and datapathes */
    char		onset_time[13];
    char		line[256];
    char		db_name[30];
    char		out_name[256];
    char		out[256];
    char		out_name1[256];
    char		out_name2[256];
    char		out_name3[256];
    char		out_namex[256];
    char		pathname[256];
    char		addname[256];
    char                tmp_fname[256];
    char                cal_path[256];
    char		lchr;
    char		station_name[6];
    char		sta_list[255];
    char		sta_li[255];
    char		time_type;
    int			ref_index;
    FILE		*fptr;
    FILE		*fphase;
    FILE		*fp,*fo,*ft;
    char		*ptr;
    int 		file_type;
/* ----------------------------------*/

    char		phase[255];
    int			io_res;
    int			res;
    int			ind;
    int			count;
    int			i,ii,j,k;
    int			a;
    int			kk,ik,uk;
    int			no_station;
    int			num;
    int			chan;
    char 		component[2];
    int			co;
    int			m_sec;

/* filetering */
    float               fcorner,f_old;   /* corner frequency of new and original seismeter */
    int			fx,fz,fy;
    float               flo,fup;
    int                 pole;
    char		zero;
    int			zorro;
    float               damp,h_old;      /* damping factors of simulated and original seismometer */
    float               gain;
/* ----------*/

/* flags for decision making */
    int                 flag;
    char 		ifilt;
    char                lfag;
    char                iflag;
    char                seidl;
    char		method ;
/* -------------------------- */

    int			row;
    int			ak;
    int			param;
    float		summ;
    float		maximum;
    double		coeff;
    double		t_coeff;
    int			shift;
    float		ampl;
    float		period;
    float		eps;
    float		rest;
    int			wslide,wlen;
    int			rot_flag;
    int			number = 0;
    int			*newclass;

/* trace buffer and other storage */
    int			*ndat;
    float		**buff;
    float		*buffer;
    double		*pick_times;
    char		**stations;
    float		**cluster;
    float		**menke;
    float		**totclust;
    float		**shifty;
    
/*-----------------------------*/

    double		start_point;
    double		end_point;
    int			start;
    int			chan_code;
    int			reall;
    int			windowlen;
    float		swindowlen;
    int			pick_len;
    int			beforepick;
    float		sbeforepick;
    int			diff;
    int			size2;
    float		*t_samp;
    int			hr1,hr2;
    int			io_new;
    int			io_done;
    int			file_found;
    int			count1 = 1;
    int			mo;
    int			first;
    int			first2;

/* variables for the polarisation vector */
    long                new_pos,end_pos;                /* longs for file positioning */
    char		dum;
    char		du[100];

    /* at first we open the database */
    io_res = FALSE;
    while(io_res != TRUE)
    {
        printf("\nEnter the name of the DATABASE: -> ");
        gets(line);
        strcpy(db_name,line);
    
        if(d_open(db_name,"o") == S_UNAVAIL)
	{
	    printf("No database with the name %s is available\n");
	    exit(1);
	}
	else
	{
	   io_res = TRUE;
	}
    }


    first = 0;

    /*----------------- enter station list -----------------*/
    printf("\nEnter station list you want extract (','seperates): -> ");
    gets(line);
    strcpy(sta_list,line);
 
/*-------------------- enter filetype -----------------*/
    printf("\nEnter filetype (GSE,ISAM,PDAS):->");
    gets(line);
    if((strcmp(line,"GSE") == 0) || (strcmp(line,"gse")    == 0))
     file_type = 200;
    if((strcmp(line,"ISAM") == 0) || (strcmp(line,"isam") == 0))
     file_type = 0;
    if((strcmp(line,"PDAS") == 0) || (strcmp(line,"pdas") == 0))
     file_type = 100;

    i = j = 0;
    while(sta_list[i] != '\0')
    {
	if (sta_list[i] == ',') j++;
	i++;
    }
    no_station = j + 1;

    stations = (char **)malloc((size_t)(no_station*sizeof(char *)));
    for(i=0;i<no_station;i++)
        stations[i] = (char *)malloc((size_t)(10*sizeof(char)));

    strcpy(sta_li,",");
    strcat(sta_li,sta_list);
    k = no_station -1;
    while (strlen(sta_li) != 0)
    {
        if (strrchr(sta_li,','))
        {
            ptr = strrchr(sta_li,',');
            ptr++;
            strcpy(stations[k],ptr);
            strcpy(station_name,ptr);
            ptr--;
            *ptr = '\0';
            k--;
        }
        else
        {
                fprintf(stderr,"ERROR reading station list\n");
                exit(-1);
        }
    }

    printf("\nWhat component do you want to use (Z/N/E)? ->");
    gets(line);
    strcpy(component,line);
    component[0]=toupper(component[0]);
    if(component[0] == 'Z')
       chan_code = 1;
    if(component[0] == 'N')
       chan_code = 2;
    if(component[0] == 'E')
       chan_code = 3;
    
    /* get a file name for output */
    printf("\nEnter the basename of output files (automatic extended): -> ");
    gets(line);
    strcpy(out_name,line);

/* simulation of a common seismometer */
    printf("\nSimulate seismometer (y/n)-> ");
    gets(line);
    seidl = line[0];
    seidl = toupper(seidl);
    if(seidl == 'Y')
    {
      printf("\nEnter corner frequency and damping of simulated instrument->");
      gets(line);
      sscanf(line,"%f,%f",&fcorner,&damp);

    }
/* -----------------------------------*/
/* filtering the traces before xcorr */
    printf("\n Filter Y/N? ->");
    gets(line);
    ifilt = toupper(line[0]);
    if(ifilt == 'Y')
    {
	printf("\nEnter low corner, high corner, nu of sections and zero phase y/n->");
	gets(line);
	sscanf(line,"%f,%f,%d,%c",&flo,&fup,&pole,&zero);

	zero = toupper(zero);

	if(zero == 'Y')
	  zorro = TRUE;
	else
	  zorro = FALSE;
    }
/**************************************/
    printf("\nEnter Phase file computing -> ");
    gets(line);
    sscanf(line,"%s",&phase);
    if((fphase = fopen(phase,"r")) == NULL)
    {
	fprintf(stderr,"FILE %s not found ... BYE\n",phase);
	exit(-1);
    }

    printf("\Enter cluster decomposition method (J-owa,H-Ruedi)-> ");
    gets(line);
    sscanf(line,"%c",&method);
    method = toupper(method);

    printf("\nEnter time type of file (Automatic,Normal,Reloc) -> ");
    gets(line);
    sscanf(line,"%c",&time_type);
    time_type = toupper(time_type);
    
    printf("\nEnter cutting window in secs (total length, before pick) -> ");
    gets(line);
    sscanf(line,"%f,%f",&swindowlen,&sbeforepick);

    printf("\nEnter xcorr threshold ->");
    gets(line);
    sscanf(line,"%lf",&t_coeff);

/********************************************************/
/* now all input variables are chosen we can start .... */
/********************************************************/

    if((envptr=getenv("IATSN_CAL")) != NULL)
    {
        strcpy(cal_path,envptr);
        if (cal_path[strlen(cal_path)-1]!='/') {
            strcat(cal_path,"/");
        }
    }
    else
    {
        strcpy(cal_path,"./");
    }

    /* get path of trace directory */
    if((envptr=getenv("IATSN_DATA")) == NULL)
    {
        printf("Environment variable IATSN_DATA not set; can't continue !\n");
        exit(1);
    }
    else
    {   
        strcpy(pathname,envptr);
    }



    j = 0;

    reall = 0;
    while(fgets(line,255,fphase) != NULL)
    {
	reall++;
    }
    rewind(fphase);

    number = reall;


    buff = (float **)malloc((size_t)(number*sizeof(float *)));
    pick_times = (double *)malloc((size_t)(number*sizeof(double )));
    k = 0;

    while(fgets(line,255,fphase) != NULL)
    {
      if(time_type == 'A')
      {
        sscanf(line,"%04d%02d%02d%02d%02d%f %04d%02d%02d%02d%02d%f %s",
		&input1.yr,&input1.mo,&input1.day,&input1.hr,&input1.mn,
		&input1.sec,&input2.yr,&input2.mo,&input2.day,&input2.hr,
		&input2.mn,&input2.sec,&du);
        start_sel = base_diff(input1);
      }
      if(time_type == 'N')
      {
      /* 
        sscanf(line,"%d,%d,%d,%d,%d,%f",
		&input1.yr,&input1.mo,&input1.day,&input1.hr,&input1.mn,
		&input1.sec);
	*/	
        sscanf(line,"%04d%02d%02d%02d%02d%f",
		&input1.yr,&input1.mo,&input1.day,&input1.hr,&input1.mn, &input1.sec);
        start_sel = base_diff(input1);
      }
      if(time_type == 'R')
      {
        sscanf(line,"%lf",&start_sel);
      }

      pick_times[k] = start_sel;
      k++;
    }
    fclose(fphase);

    totclust =  matrix(1,number,1,number);

/*****************************************/
   for(uk = 0; uk < no_station; uk++)
   {
        ndat = (int *)calloc(reall,sizeof(int *));
        t_samp = (float *)calloc(reall,sizeof(float *));
        cluster =  matrix(1,number,1,number);
        menke =  matrix(1,number,1,number);
        shifty =  matrix(1,number,1,number);

	io_new = FALSE;
	first = -1;
        for(k = 0; k<reall; k++)
        {
	   buff[k] = (float *)calloc(1,sizeof(float));
	   first2 = 0;
   	   for(d_keyfrst(STATION_STATION_KEY, CURR_DB);db_status == S_OKAY; d_keynext(STATION_STATION_KEY, CURR_DB))
    	   {
            d_recread(&station, CURR_DB);
            d_crget(&dba, CURR_DB);
            d_setor(STATION_SET, CURR_DB);
            num = strlen(stations[uk]);
             if((strncmp(station.stat_code,stations[uk],num)==0) && (station.chan_code == chan_code))
             {
                for(d_findfm(STATION_SET, CURR_DB); db_status == S_OKAY; d_findnm(STATION_SET, CURR_DB))
                {
                    d_recread(&trace_rec_a, CURR_DB);
                    t_samp[k] = trace_rec_a.t_samp;
                    ndat[k]= (int)((trace_rec_a.end_time -
                            trace_rec_a.start_time)/trace_rec_a.t_samp)+1;
                    rest = t_samp[k];
		    beforepick = (int)(sbeforepick/t_samp[k]);
		    windowlen = (int)(swindowlen/t_samp[k]);
		    buff[k] = (float *)realloc(buff[k],windowlen*sizeof(float));
                    start_point = (pick_times[k] - trace_rec_a.start_time)/t_samp[k];
                    start_point = start_point- (double)beforepick -1.;
                    end_point = (trace_rec_a.end_time - pick_times[k])/t_samp[k] + (double)beforepick - (double)windowlen; 
                    if((start_point > 0) && (end_point > 0))
                    {
		        first2 = 1;
                        io_done = TRUE;
                        if(station.chan_code == chan_code)
                                start = (int)(start_point+0.5);
                        if(io_new == TRUE)
                        {
                            if(fabs(trace_rec_a.start_time-start_time_old) > rest)
                            {
                                io_new = FALSE;
	    			file_found = FALSE;
				free((char *)buffer);
                            }
                        }
                    }
                    else
                    {
                        io_done = FALSE;
                    }
		    if(io_done == TRUE)
		    {
			if(io_new == FALSE)
			{
  			     if(seidl == 'Y')
			     {
        		          d_crset(&dba, CURR_DB);
                                  if(d_isowner(CALIBRATION_SET, CURR_DB) == S_OKAY)
                                  {
                                      d_setor(CALIBRATION_SET, CURR_DB);
                                      for(d_findfm(CALIBRATION_SET, CURR_DB); db_status == S_OKAY;
                                              d_findnm(CALIBRATION_SET, CURR_DB))
                                      {
                                          d_recread(&tmp_cal,CURR_DB);
                                          if((tmp_cal.start_time <= pick_times[k]) &&
                                                  (tmp_cal.end_time >= pick_times[k]))
                                          {
                                               /***********************************/
                                               /* now we found the first cal file */
                                               /* we have to be sure that the next*/
                                               /* one is outside the time range   */
                                               /* if not we have to different cal */
                                               /* files for the station......     */
                                               /***********************************/
                                               d_findnm(CALIBRATION_SET,CURR_DB);
                                               if (db_status == S_OKAY) 
					       {
                                                  d_recread(&check_cal,CURR_DB);
                                                  if ((check_cal.start_time <= pick_times[k]) &&
                                                        (check_cal.end_time >= (pick_times[k] + (float)(ndat[k]/t_samp[k])))) 
						  {
                                                     fprintf(stderr,"Next Calibration lies also in selected time range, we can't manage this!\n Do nothing\n!");
                                                     d_freeall();
                                                     goto do_escape;
                                                  }
					       }
                                               else {
                                                  fprintf(stderr,"This was the last cal record in set\n");

                                               }
                                               memcpy((void *)&calib
						,(void *)&tmp_cal,1*sizeof(Calibration));
                                               fprintf(stderr,"Found a single Calibration for station - GOOD\n");
                                               break;
                                           }
                                           strcpy(tmp_cal.cal_name,"unknown.cal");
                                       }
            
                                       if(!strcmp(tmp_cal.cal_name,"unknown.cal"))
                                       {
                                           fprintf(stderr,"No calibration file found for a trace\n");

                                       }
                                 }
                              }

			      if(station.chan_code == chan_code)
			      {
                                 start_time_old = trace_rec_a.start_time;
                                 strcpy(addname,pathname);
                                 strcat(addname,trace_rec_a.file_name);
                                 if((fptr = fopen(addname,"rb")) == NULL)
                                 {
                                     printf("Cannot open file %s\n",addname);
                                     exit(-1);
                                 }
                                 fclose(fptr);
 
                                 buffer=(float *)calloc(ndat[k],sizeof(float));
                                 if(read_trace_to_buffer(addname,buffer,0,ndat[k],file_type) != TRUE)
                                 {
                                    printf("Unable to open file, set to 0...\n");
				    file_found = FALSE;
				
                                 }
				 else
				    file_found = TRUE;
			      }

 	       		      if(seidl == 'Y' && file_found == TRUE)
	       		      {
                   		      strcpy(tmp_fname,cal_path);
                   		      strcat(tmp_fname,calib.cal_name);
                   		      read_pazfile(tmp_fname,&f_old,&h_old,&gain);
                   		      for(ii = 0; ii < ndat[k];ii++)
                       		      buffer[ii] /= gain;
                         
                   		      off_rem(buffer,ndat[k]);
                   		      simfilt(buffer,ndat[k],t_samp[k],f_old,fcorner,-1.,h_old,damp,-1.,0);
                	      }

	        	      if(ifilt == 'Y' && file_found == TRUE)
	        	      {
                    		      spr_bp_fast_bworth(buffer,ndat[k],t_samp[k],flo,fup,pole,zorro);
	        	      }

	                      io_new = TRUE;
		    } /* end of io_new */


	     if(file_found == TRUE)
	     {

		diff = 0;
		if(start < 0)
		{
		    start = 0;
		}
		if((start+windowlen) >= ndat[k] )
		{
		     diff = start+windowlen - (ndat[k]-1);
		}

		
		memcpy((char *)buff[k],(char *)(buffer+start),(windowlen-diff)*sizeof(float));
	        off_rem(buff[k],(windowlen-diff));
		if(diff > 0){
		   for(ii=(windowlen-diff);ii< windowlen; ii++) buff[k][ii] = 0.0;
		}
	    }else
	    {
	    }

           } /* end of io_done */

	    io_done = FALSE;

   	  } /* end of STATION SET */
	} /* end of if station */
       } /* end of for station key loop */   
       if(first2 == 0){
	   	buff[k]=(float *)realloc(buff[k],windowlen*sizeof(float));
		for(ii=0;ii<windowlen;ii++)
		   buff[k][ii] = 0.0;
       }

      } /* for all phases */
	io_new = FALSE;
	io_done = FALSE;
	file_found = FALSE;

/*****************************************************/
/* now we are ready to perform the xcorrelation and  */
/* write out the matrix and the cluster traces       */
/*****************************************************/
	strcpy(out,out_name);
	strcat(out,stations[uk]);
	strcat(out,component);
        if((fo = fopen(out,"w")) == NULL)
        {
           fprintf(stderr,"\nCan't open %s for output .....Bye\n",out);
           exit(-1);
        }
         
        for(i=0;i<number;i++)
        {
           for(j=i;j<number;j++)
           {
                if(((t_samp[i]-t_samp[j])>1.e-6))
                {
                    fprintf(stderr,"\nNot the same sampling rate");
                    fprintf(stderr,"\nadding 0 for pair %d:%d",(i+1),(j+1));
                    fprintf(fo,"%d %d %f %d\n",(i+1),(j+1),0,0);
                }
                else
                {
                   param = windowlen/2;
		   if(i!=j)
                     X_corr(buff[i],buff[j],param,windowlen,windowlen,&shift,&coeff);
		   else
		   {
		      coeff = 1.0;
		      shift = 0;
		   }
                   if(fabs(coeff) > t_coeff)
                   {
                        fprintf(fo,"%d %d %f %d\n",(i+1),(j+1),(float)fabs(coeff),shift);             
                        shifty[i+1][j+1] = (float)shift;
                        shifty[j+1][i+1] = (float)shift;
                        cluster[i+1][j+1] = 1.0;
                        cluster[j+1][i+1] = 1.0;
			menke[i+1][j+1] = fabs(coeff);
			menke[j+1][i+1] = fabs(coeff);
			if(uk == 0)
			{
			    totclust[i+1][j+1] = 1.0;
			    totclust[j+1][i+1] = 1.0;
			}
			else
			{
			    totclust[i+1][j+1] *= 1.0;
			    totclust[j+1][i+1] *= 1.0;
			}
                   }
                   else
                   {
                        shift = 0;
                        coeff = 0.;
                        fprintf(fo,"%d %d %f %d\n",(i+1),(j+1),(float)fabs(coeff),shift);
                        cluster[i+1][j+1] = 0.0;
                        cluster[j+1][i+1] = 0.0;
			menke[i+1][j+1] = fabs(coeff);
			menke[j+1][i+1] = fabs(coeff);

			if(uk == 0)
			{
			    totclust[i+1][j+1] = 0.0;
			    totclust[j+1][i+1] = 0.0;
			}
			else
			{
			    totclust[i+1][j+1] *= 0.0;
			    totclust[j+1][i+1] *= 0.0;
			}
                   }
                }
            }
        }      
        fclose(fo);
        strcpy(out_name1,out);
        strcpy(out_name2,out);
        strcpy(out_name3,out);
        strcat(out_name1,".matrix");
        strcat(out_name2,".cluster");
        strcat(out_name3,".menke");
        if((fp = fopen(out_name1,"w")) == NULL)
        {
                fprintf(stderr,"Can't open %s .. Bye\n",out_name1);
                exit(-1);
        }
        if((fo = fopen(out_name2,"w")) == NULL)
        {
                fprintf(stderr,"Can't open %s .. Bye\n",out_name2);
                exit(-1);
        }
        if((ft = fopen(out_name3,"w")) == NULL)
        {
                fprintf(stderr,"Can't open %s .. Bye\n",out_name3);
                exit(-1);
        }
        if(method == 'J')
        {
          maximum = 3.0;
          first = 0;
 
          while(maximum > 2.0)
          {
           maximum = 0.;
           row = 0;
           for(i=1;i<=number;i++)
           {
                summ = 0.0;
                for(j=1;j<=number;j++)
                {
                   summ += cluster[i][j];
                   if((first == 0) && (cluster[i][j] >0.))
                     fprintf(fp,"%d %d %f\n",i,j,cluster[i][j]);

                   if((first == 0) && (i != j))
                     fprintf(ft,"%f\n",menke[i][j]);
                }
                if(summ > maximum)
                {
                   maximum = summ;
                   row = i;
                }
           }
           first = 1;
           if(maximum > 2.)
           {
             for(j=1;j<=number;j++)
             {
                if(cluster[row][j] >0.)
		{
		   onset_t = do2date(pick_times[j-1]-(double)(shifty[row][j]*t_samp[j-1]));
                   fprintf(fo,"%d %d %f %d %04d%02d%02d%02d%02d%f\n"
			,row,j,cluster[row][j],(int)shifty[row][j],
			onset_t.yr,onset_t.mo,onset_t.day,onset_t.hr,
			onset_t.mn,onset_t.sec);
		}
             }
 
             for(i=1;i<=number;i++)
             {
                if(i!=row)
                {
                  for(j=1;j<=number;j++)
                  {
                     if((cluster[i][j] > 0.) && (cluster[row][j] >0.))
                        cluster[i][j] = 0.;
                  }
                }
             }
             for(j=1;j<=number;j++)
                cluster[row][j] = 0.;
           }   
         }
        
        }
	else{
		/******************************************/
		/* Cluster Decomposition after Hans-Ruedi */
		/******************************************/

	   /* writing out the matrix first */
	
	   for(i=1;i<=number;i++)
	   {
	       	for(j=1;j<=number;j++)
	       	{
                   if(cluster[i][j] >0.)
                     fprintf(fp,"%d %d %f\n",i,j,cluster[i][j]);

                   if(i != j)
                     fprintf(ft,"%f\n",menke[i][j]);
		}
	   }
		  
	   /* now find the cluster */
	   row = 0;
	   for(i=1;i<=number;i++)
	   {
	        newclass = (int *)malloc((size_t)(1*sizeof(int)));
	        a = 1;
		first = 0;
		for(j=1;j<=number;j++)
		{
		    if(cluster[i][j] > 1.0)
		    {
			first++;
		    } 
		}
		if(first > 0)
		{
		   newclass[a-1] = i;
		   a++;
		}

		for(j=i+1;j<=number;j++)
		{
		   summ = 0.;
		   for(k=1;k<=number;k++)
		   {
		     summ += cluster[i][k]*cluster[j][k];
		   }
		
		   if(summ > 1.)
		   {
			newclass = (int *)realloc(newclass,a*sizeof(int));
			newclass[a-1] = j;
			a++;

			for(k=1;k<=number;k++)
			{
			    cluster[j][k] = 0.;
			}
		    }
		 }

		 if(a>2)
		 {
		  row++;
		  for(k=0;k<a-1;k++)
		  {
		      onset_t = do2date(pick_times[newclass[k]-1]);
                      fprintf(fo,"%d %d %04d%02d%02d%02d%02d%f\n"
			,row,newclass[k],
			onset_t.yr,onset_t.mo,onset_t.day,onset_t.hr,
			onset_t.mn,onset_t.sec);
		  }
		 }
	         
		 free((char *)newclass);

	  }
	} /* end of HR Decom */
 
        fclose(fo);
        fclose(fp);
	fclose(ft);

	for(k = 0; k < reall; k++)
	{
	     free((char *)buff[k]);
	}
	free((char *)ndat);
	free((char *)t_samp);
	free_matrix(cluster,1,number,1,number);
	free_matrix(menke,1,number,1,number);
	free_matrix(shifty,1,number,1,number);
	free((char *)buffer);

    }  /* for all stations */

    strcpy(out_name2,out);
    strcat(out_name2,".tcluster");
    if((fo = fopen(out_name2,"w")) == NULL)
    {
          fprintf(stderr,"Can't open %s .. Bye\n",out_name2);
          exit(-1);
    }
    strcpy(out_namex,out);
    strcat(out_namex,".tmatrix");
    if((ft = fopen(out_namex,"w")) == NULL)
    {
          fprintf(stderr,"Can't open %s .. Bye\n",out_namex);
          exit(-1);
    }

/*first we write out the stacked matrix */

    for(i=1;i<=number;i++)
    {
         for(j=1;j<=number;j++)
        {
          if(totclust[i][j] >0.)
            fprintf(ft,"%d %d %f\n",i,j,totclust[i][j]);
	}
    }

/* now we try to decompose the different classes */

    if(method == 'J')
    {
       maximum = 3.0;
       first = 0;
 
       while(maximum > 2.0)
       {
          maximum = 0.;
          row = 0;
          for(i=1;i<=number;i++)
          {
              summ = 0.0;
              for(j=1;j<=number;j++)
              {
                 summ += totclust[i][j];
              }
              if(summ > maximum)
              {
                 maximum = summ;
                 row = i;
              }
           }
	   first = 1;

           if(maximum > 2.)
           {
             for(j=1;j<=number;j++)
             {
                if(totclust[row][j] > 0.)
		{
		   onset_t = do2date(pick_times[j-1]);
                   fprintf(fo,"%d %d %f %d %04d%02d%02d%02d%02d%f\n"
			,row,j,totclust[row][j],0,
			onset_t.yr,onset_t.mo,onset_t.day,onset_t.hr,
			onset_t.mn,onset_t.sec);
		}
             }
 
             for(i=1;i<=number;i++)
             {
                if(i!=row)
                {
                  for(j=1;j<=number;j++)
                  {
                     if((totclust[i][j] > 0.) && 
				(totclust[row][j] > 0.))
                        totclust[i][j] = 0.;
                  }
                }
             }
             for(j=1;j<=number;j++)
                totclust[row][j] = 0.;
           }   
        }
        
    }
    else
    {
		/******************************************/
		/* Cluster Decomposition after Hans-Ruedi */
		/******************************************/

	   /* now find the totclust */
	   row = 0;
	   for(i=1;i<=number;i++)
	   {

	        newclass = (int *)malloc((size_t)(1*sizeof(int)));
	        a = 1;
		first = 0;
		for(j=1;j<=number;j++)
		{

		    if(totclust[i][j] > 1.0)
		    {
			first++;
		    } 
		}
		if(first > 0)
		{
		   newclass[a-1] = i;
		   a++;
		}

		for(j=i+1;j<=number;j++)
		{
		   summ = 0.;
		   for(k=1;k<=number;k++)
		   {
		     summ += totclust[i][k]*totclust[j][k];
		   }
		
		   if(summ > 1.)
		   {
			newclass = (int *)realloc(newclass,a*sizeof(int));
			newclass[a-1] = j;
			a++;

			for(k=1;k<=number;k++)
			{
			    totclust[j][k] = 0.;
			}
		    }
		 }

		 if(a>2)
		 {
		  row++;
		  for(k=0;k<a-1;k++)
		  {
		      onset_t = do2date(pick_times[newclass[k]-1]);
                      fprintf(fo,"%d %d %04d%02d%02d%02d%02d%f\n"
			,row,newclass[k],
			onset_t.yr,onset_t.mo,onset_t.day,onset_t.hr,
			onset_t.mn,onset_t.sec);
		  }
		 }
	         
		 free((char *)newclass);
	  }
    }

    fclose(fo);
    fclose(ft);

    free_matrix(totclust,1,number,1,number);
 
    d_close(CURR_DB);

do_escape:
	if(io_done == TRUE)
	{
		  for(k = 0; k < number; k++)
		  {
		     free((char *)buff[k]);
		  }
	}
	d_close(CURR_DB);

}

