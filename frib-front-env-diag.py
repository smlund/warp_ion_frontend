
# choose whether to integrate the ode using real-time warp data

integratewarp = 0 # 0: no, 1: yes

# plot envelopes of the two species with highest and lowest rigidities
# 0: false, 1: true

plot_extreme_brho = 1 

# The following diagnostic functions make the respective plots for a particular species

# envelope: plot the envelope from both Warp and the Env. Model
# env_terms: plot the terms in the Envelope Equation as calculated by the Env. Model
# warp_terms: plot the terms in the Envelope Equation as calculated by WARP
# env_vs_warp: a series of 5 plots, each ploting the same term from both the Env. Model and WARP
# terms_diff: plot the difference between the Env. Model terms and the WARP terms
# ke_diff: plot the difference in KE between the Env. Model and WARP

# lists specifying the species (by name) to which each function should be applied

species_envelope = ["all"]  # use "all" to plot every species or specify the desired species

species_env_terms = ["U33"]

species_warp_terms = ["U33"]

species_env_vs_warp = ["U33"]

species_terms_diff = ["U33"]

species_ke_diff = ["U33", "U34"]























## Compute the terms in the Env. Model using real-time WARP data

termdatawarp = []

for iii in range(0, top.jhist+1):
	
	xyz = 0
	
	zzz = top.hzbeam[iii]
	deltaz = diff(top.hzbeam)[0]/2
	
	efieldz = getappliedfields(0, 0, zzz)[2][0]
	bfieldz = getappliedfields(0, 0, zzz)[5][0]
	dEdz = (getappliedfields(0, 0, zzz + deltaz/2)[2][0] - getappliedfields(0, 0, zzz - deltaz/2)[2][0])/deltaz
	
	kelist = array([hl_ekin[iii,j] for j in range(top.ns)])
	speciesbeta = array([sqrt((2*kelist[j]*jperev)/(specieslist[j].mass*clight**2)) for j in range(top.ns)])
	anglelist = array([top.hxxpbar[0,iii,j]/(top.hxrms[0,iii,j])*sqrt(2) for j in range(top.ns)])
	envelopelist = array([top.hxrms[0,iii,j]*sqrt(2) for j in range(top.ns)])
	pthetalist = array([hl_pthn[iii,j] for j in range(top.ns)])
	
	xyz = concatenate((kelist, envelopelist, anglelist))
	
	## Set the neutralization factor
	
	neut_ode = get_neut(zzz)
	
	for j in range(top.ns):
				
		scterm = 0
		
		for s in range(top.ns):
			QQQ = (speciesq[j]*speciesI[s])/(2*pi*eps0*specieslist[j].mass*speciesbeta[j]**2*speciesbeta[s]*clight**3)
			scterm += QQQ*neut_ode*xyz[j+top.ns]/(xyz[j+top.ns]**2 + xyz[s+top.ns]**2)
		
		term1 = (speciesq[j]*-efieldz)/(2*xyz[j]*jperev) * xyz[j+2*top.ns]
		
		term2 = (speciesq[j]*-dEdz)/(4*xyz[j]*jperev) * xyz[j+top.ns]
		
		term3 = ((speciesq[j]*bfieldz)/(2*specieslist[j].mass*speciesbeta[j]*clight))**2*xyz[j+top.ns]

		emitterm = ((top.hepsr[0,iii,j]/2)**2 + (pthetalist[j] /speciesbeta[j])**2) / xyz[j+top.ns]**3
		
		#d2sigmadz2 = term1 + term2 - term3 + scterm + emitterm
		
		#derivs.append(d2sigmadz2)
		
		termdatawarp.append([j, zzz, term1, term2, -term3, scterm, emitterm, xyz[j]])









from scipy import interpolate

state_vector_2 = [0]*3*top.ns

dct = {}

deltaz = stepsize/2.



## Set up function used to integrate the Env. Model using real-time WARP data

zlist = []
		
zlist = array([top.hzbeam[kkk] for kkk in range(0, top.jhist+1)])

def fwarp(state_vector_2, rrr):
	
	efieldz = getappliedfields(0, 0, rrr)[2][0]
	bfieldz = getappliedfields(0, 0, rrr)[5][0]
	
	dEdz = (getappliedfields(0, 0, rrr + deltaz/2)[2][0] - getappliedfields(0, 0, rrr - deltaz/2)[2][0])/deltaz
	#dVdz = 0
	
	derivs = []
	
	for i in range(U_ns):
		derivs.append(U_species[i].charge/jperev*efieldz) #build first lot in deriv output
	
	for i in range(O_ns):
		derivs.append(O_species[i].charge/jperev*efieldz) #build first lot in deriv output
	
	for i in range(top.ns):
		derivs.append(state_vector_2[i+2*top.ns]) #build second lot in deriv output
	
	speciesbeta = []
	
	for i in range(top.ns):
		speciesbeta.append(sqrt((2*state_vector_2[i]*jperev)/(specieslist[i].mass*clight**2)))

	## Set the neutralization factor
	
	neut_ode = get_neut(rrr)

	for j in range(top.ns):
		
		scterm = 0
		
		
		
		emittancelist = []
		
		#for kkk in range(len(top.hepsr)):
			#emittancelist = emittancelist.append(top.hepsr[0,kkk,j])
		
		emittancelist = array([top.hepsr[0,kkk,j]/2 for kkk in range(0, top.jhist+1)])
		
		pthetaLIST = []
		
		pthetaLIST = array([hl_pthn[kkk,j] for kkk in range(0, top.jhist+1)])
		
		kineticenergylist = []
		
		kineticenergylist = array([hl_ekin[kkk,j] for kkk in range(0, top.jhist+1)])
		

		emitinter = interpolate.interp1d(zlist, emittancelist, kind='slinear')
		
		pthetainter = interpolate.interp1d(zlist, pthetaLIST, kind='slinear')
		
		keinter = interpolate.interp1d(zlist, kineticenergylist, kind='slinear')
		
		for s in range(top.ns):
			QQQ = (speciesq[j]*speciesI[s])/(2*pi*eps0*specieslist[j].mass*speciesbeta[j]**2*speciesbeta[s]*clight**3)
			scterm += QQQ*neut_ode*state_vector_2[j+top.ns]/(state_vector_2[j+top.ns]**2 + state_vector_2[s+top.ns]**2)
		
		term1 = (speciesq[j]*-efieldz)/(2*state_vector_2[j]*jperev) * state_vector_2[j+2*top.ns]
		
		term2 = (speciesq[j]*-dEdz)/(4*state_vector_2[j]*jperev) * state_vector_2[j+top.ns]
		
		term3 = ((speciesq[j]*bfieldz)/(2*specieslist[j].mass*speciesbeta[j]*clight))**2*state_vector_2[j+top.ns]

		emitterm = ((emitinter(rrr))**2 + (pthetainter(rrr) /speciesbeta[j])**2) / state_vector_2[j+top.ns]**3
		
		d2sigmadz2 = term1 + term2 - term3 + scterm + emitterm
		
		derivs.append(d2sigmadz2)
		
	return derivs
		
		
if integratewarp == 1:
	psolnwarp = odeint (fwarp, initialstates, sss, hmax = stepsize, mxstep=5000)













termdata2 = []
termdatawarp2=[]

for i in range(0, len(termdata), 20):
	termdata2.append(termdata[i])

termdata2 = array(termdata2)

termdatawarp2 = array([termdatawarp[i] for i in  range(0, len(termdatawarp), 20)])




# --- Target Species, x-plane 
hpenvx(titles=false,yscale=1./(2.*mm),lhzbeam=true)
lab = ""    
for ii in sp_target:
      s = sp[ii]
      js = s.js
      co = s.color
      lab+= ii + "("+co+"), "
      hpenvx(js=js,color=co,titles=false,yscale=1./(2.*mm),lhzbeam=true)    
ptitles("Env. Model (dashed), Warp (solid)","z [m]","RMS x-Envelope [mm]", )

plg(psoln[:,20]*1000/sqrt(2),sss, color="magenta", type="dash")
plg(psoln[:,21]*1000/sqrt(2),sss, color="green", type="dash")
#limits(plotxmin,plotxmax, plotymin, plotymax)


combinedenvelop = [0]*stepnum

totalweight=0.
for j in specieslist:
	totalweight += j.sw

for i in range(stepnum):
	
	SumofR2overN = 0.
	
	for j in range(top.ns):
		#combinedenvelop[i] += psoln[i, j+top.ns]*1000/sqrt(2)*speciesI[j]/sum(speciesI)
		SumofR2overN += psoln[i, j+top.ns]**2*(specieslist[j].sw/totalweight)
	
	combinedenvelop[i] = SumofR2overN**0.5*1000/sqrt(2)

plg(combinedenvelop,sss, color="black", type="dash")

fma()	








def envelope(iii):
    s = sp[iii]
    js = s.js
    co = s.color
    hpenvx(js=js,color=co,titles=false,yscale=1./(2.*mm),lhzbeam=true)
    
    plg(psoln[:,js+20]*1000/sqrt(2),sss, color=co, type="dash")
    ptitles("Env. Model (dashed), Warp (solid), %s" % iii,"z [m]","RMS x-Envelope [mm]", )
    #limits(plotxmin,plotxmax, plotymin, plotymax)
    
    fma()



if plot_extreme_brho == 1:

	brho_selection = hl_brho[0]
	
	max_value = max(brho_selection)
	max_index = nanargmax(brho_selection)
	
	for iii in sp:
		s = sp[iii]
		if max_index == s.js:
			hpenvx(js=js,color='black',titles=false,yscale=1./(2.*mm),lhzbeam=true)
			plg(psoln[:,js+20]*1000/sqrt(2),sss, color='black', type="dash")
			name1 = s.name
	
	min_value = min(brho_selection)
	min_index = nanargmin(brho_selection)
	
	for iii in sp:
		s = sp[iii]
		if min_index == s.js:
			hpenvx(js=js,color='red',titles=false,yscale=1./(2.*mm),lhzbeam=true)
			plg(psoln[:,js+20]*1000/sqrt(2),sss, color='red', type="dash")
			name2 = s.name
	
	
	ptitles("Species with extreme rigidities, max(black): %s, min(red): %s" % (name1, name2),"z [m]","RMS x-Envelope [mm]", )
	#limits(plotxmin,plotxmax, plotymin, plotymax)
	
	fma()




if species_envelope[0] == "all":
	for jjj in sp:
		envelope(jjj)
else:
	for jjj in species_envelope:
		envelope(jjj)










for ii in sp_target:
      s = sp[ii]
      js = s.js
      co = s.color
      A  = s.mass/amu
      #hpekin(js=js,color=co,titles=false,yscale=1./A,lhzbeam=true)
      plg(hl_ekin[0:top.jhist+1,js]/(A*kV),top.hzbeam[0:top.jhist+1],color=co)        
ptitles("Kinetic Energy, Env. Model (dashed), Warp (solid)","z [m]","KeV/u", )

plg(psoln[:,0]/1000/238.02891,sss, color="magenta", type="dash")
plg(psoln[:,1]/1000/238.02891,sss, color="green", type="dash")

fma()



# --- Target Species, x-plane 
#lab = ""    
#for ii in sp_target:
      #s = sp[ii]
      #js = s.js
      #co = s.color
      #lab+= ii + "("+co+"), "
      #plg(top.hepsr[0, 0:top.jhist+1,js]*CorrectionFactor,top.hzbeam[0:top.jhist+1],color=co)
      #plg(sqrt(4*top.hepsx[0, 0:top.jhist+1,js]**2 - hl_lz_bar2[0:top.jhist+1,js]**2),top.hzbeam[0:top.jhist+1],color=co, type="dash")    
#ptitles("History: "+lab+"RMS x-Envelope","z [m]","RMS Width [mm]", )

#fma()




## Plot the terms in the Envelope Equation as calculated by the Env. Model

def env_terms(ii):
	
	jj = sp[ii].js
	
	termdata4 = []
	termdatawarp4=[]

	
	termdata4 = array([termdata[i] for i in range(jj, len(termdata), top.ns)])

	termdatawarp4 = array([termdatawarp[i] for i in  range(jj, len(termdatawarp), top.ns)])
	
	plg(termdata4[:,2], termdata4[:,1], color="black", type="dash")
	plg(termdata4[:,3], termdata4[:,1], color="green")
	plg(termdata4[:,4], termdata4[:,1], color="black")
	plg(termdata4[:,5], termdata4[:,1], color="red")
	plg(termdata4[:,6], termdata4[:,1], color="blue")
	
	ptitles("%s Env. Model Terms, black-dash:E green:dEdz black:B red:SC blue:Emit" % ii,"z [m]","sigma'' [rad/m]",)
	
	fma()


for iii in species_env_terms:
	env_terms(iii)




## Plot the terms in the Envelope Equation as calculated by the WARP

def warp_terms(ii):
	
	jj = sp[ii].js
	
	termdata4 = []
	termdatawarp4=[]

	
	termdata4 = array([termdata[i] for i in range(jj, len(termdata), top.ns)])

	termdatawarp4 = array([termdatawarp[i] for i in  range(jj, len(termdatawarp), top.ns)])
	
	plg(termdatawarp4[:,2], termdatawarp4[:,1], color="black", type="dash")
	plg(termdatawarp4[:,3], termdatawarp4[:,1], color="green")
	plg(termdatawarp4[:,4], termdatawarp4[:,1], color="black")
	plg(termdatawarp4[:,5], termdatawarp4[:,1], color="red")
	plg(termdatawarp4[:,6], termdatawarp4[:,1], color="blue")
	
	ptitles("%s WARP terms, black-dash:E green:dEdz black:B red:SC blue:Emit" % ii,"z [m]","sigma'' [rad/m]",)
	
	fma()

for iii in species_warp_terms:
	warp_terms(iii)





## Compare the value of each term in the Envelope Equation from WARP and Env. Model

def env_vs_warp(ii):
	
	jj = sp[ii].js
	
	termdata3 = []
	termdatawarp3=[]

	for i in range(jj, len(termdata), top.ns):
		termdata3.append(termdata[i])

	termdata3 = array(termdata3)

	termdatawarp3 = array([termdatawarp[i] for i in  range(jj, len(termdatawarp), top.ns)])


	plg(termdata3[:,2],termdata3[:,1])
	plg(termdatawarp3[:,2],termdatawarp3[:,1], type="dash")
	ptitles("%s Term 1 (E-field), Env. Modelinput (solid), WARPinput (dashed)" % ii,"z [m]","sigma'' [rad/m]",)
	fma()
	
	plg(termdata3[:,3],termdata3[:,1])
	plg(termdatawarp3[:,3],termdatawarp3[:,1], type="dash")
	ptitles("%s Term 2 (dEdz), Env. Modelinput (solid), WARPinput (dashed)" % ii,"z [m]","sigma'' [rad/m]",)
	fma()
	
	plg(termdata3[:,4],termdata3[:,1])
	plg(termdatawarp3[:,4],termdatawarp3[:,1], type="dash")
	ptitles("%s Term 3 (B-field), Env. Modelinput (solid), WARPinput (dashed)" % ii,"z [m]","sigma'' [rad/m]",)
	fma()
	
	plg(termdata3[:,5],termdata3[:,1])
	plg(termdatawarp3[:,5],termdatawarp3[:,1], type="dash")
	ptitles("%s Space Charge Term, Env. Modelinput (solid), WARPinput (dashed)" % ii,"z [m]","sigma'' [rad/m]",)
	fma()
	
	plg(termdata3[:,6],termdata3[:,1])
	plg(termdatawarp3[:,6],termdatawarp3[:,1], type="dash")
	ptitles("%s Emittance Term, Env. Modelinput (solid), WARPinput (dashed)" % ii,"z [m]","sigma'' [rad/m]",)
	fma()

for iii in species_env_vs_warp:
	env_vs_warp(iii)










## Plot the difference between the Env. Model terms and the WARP terms

def terms_diff(ii):
	
	jj = sp[ii].js
	
	termdata4 = []
	termdatawarp4=[]

	
	termdata4 = array([termdata[i] for i in range(jj, len(termdata), top.ns)])

	termdatawarp4 = array([termdatawarp[i] for i in  range(jj, len(termdatawarp), top.ns)])
	
	warpterm1inter = interpolate.interp1d(termdatawarp4[:,1], termdatawarp4[:,2], bounds_error = False, fill_value = 0., kind='linear')
	warpterm2inter = interpolate.interp1d(termdatawarp4[:,1], termdatawarp4[:,3], bounds_error = False, fill_value = 0., kind='linear')
	warpterm3inter = interpolate.interp1d(termdatawarp4[:,1], termdatawarp4[:,4], bounds_error = False, fill_value = 0., kind='linear')
	warpscterminter = interpolate.interp1d(termdatawarp4[:,1], termdatawarp4[:,5], bounds_error = False, fill_value = 0., kind='linear')
	warpemitterminter = interpolate.interp1d(termdatawarp4[:,1], termdatawarp4[:,6], bounds_error = False, fill_value = 0., kind='linear')
	
	warpterm1 = array([ warpterm1inter(kkk) for kkk in termdata4[:,1] ])
	warpterm2 = array([ warpterm2inter(kkk) for kkk in termdata4[:,1] ])
	warpterm3 = array([ warpterm3inter(kkk) for kkk in termdata4[:,1] ])
	warpscterm = array([ warpscterminter(kkk) for kkk in termdata4[:,1] ])
	warpemitterm = array([ warpemitterminter(kkk) for kkk in termdata4[:,1] ])
	
	if len(termdata4[:,2]) != len(warpterm1):
		print "termdata4[:,2] not same length as warpterm1"
	
	term1diff = termdata4[:,2] - warpterm1
	term2diff = termdata4[:,3] - warpterm2
	term3diff = termdata4[:,4] - warpterm3
	sctermdiff = termdata4[:,5] - warpscterm
	emittermdiff = termdata4[:,6] - warpemitterm
	
	plg(term1diff, termdata4[:,1], color="black", type="dash")
	plg(term2diff, termdata4[:,1], color="green")
	plg(term3diff, termdata4[:,1], color="black")
	plg(sctermdiff, termdata4[:,1], color="red")
	plg(emittermdiff, termdata4[:,1], color="blue")
	
	ptitles("%s Env. Modelinput minus WARPinput for different terms" % ii,"z [m]","sigma'' [rad/m]",)
	
	fma()

for iii in species_terms_diff:
	terms_diff(iii)




## Plot the KE of a species from WARP and Env. Model

def ke_diff(ii):
	
	jj = sp[ii].js
	
	termdata4 = []
	termdatawarp4=[]

	
	termdata4 = array([termdata[i] for i in range(jj, len(termdata), top.ns)])

	termdatawarp4 = array([termdatawarp[i] for i in  range(jj, len(termdatawarp), top.ns)])
	
	warpkeinter = interpolate.interp1d(termdatawarp4[:,1], termdatawarp4[:,7], bounds_error = False, fill_value = 0., kind='linear')
	
	warpke = array([ warpkeinter(kkk) for kkk in termdata4[:,1] ])
	
	if len(termdata4[:,2]) != len(warpke):
		print "termdata4[:,2] not same length as warpterm1"
	
	kediff = termdata4[:,7] - warpke
	
	kediffcut = array(kediff[4:-4])
	warpkecut = array(warpke[4:-4])
	
	kepercentagediff = kediffcut/warpkecut*100
	
	if jj == 0:
		plg(kepercentagediff, termdata4[:,1][4:-4], color="magenta")
	elif jj == 1:
		plg(kepercentagediff, termdata4[:,1][4:-4], color="green")
	else:
		plg(kepercentagediff, termdata4[:,1][4:-4], color="black")
	

for iii in species_ke_diff:
	ke_diff(iii)

ptitles("KE Difference between Env. Model and WARP","z [m]","% difference",)
	
fma()




if integratewarp == 1:
	
	
	
	## Env. Model with WARP input versus WARP Simulations

	# --- Target Species, x-plane 
	hpenvx(titles=false,yscale=1./(2.*mm),lhzbeam=true)
	lab = ""    
	for ii in sp_target:
	      s = sp[ii]
	      js = s.js
	      co = s.color
	      lab+= ii + "("+co+"), "
	      hpenvx(js=js,color=co,titles=false,yscale=1./(2.*mm),lhzbeam=true)    
	ptitles("Env. Model with WARP input (dashed), WARP Simulations (solid)","z [m]","RMS x-Envelope [mm]", )
	
	plg(psolnwarp[:,20]*1000/sqrt(2),sss, color="magenta", type="dash")
	plg(psolnwarp[:,21]*1000/sqrt(2),sss, color="green", type="dash")
	
	
	combinedenvelop = [0]*stepnum
	
	TotalWeight=0.
	for j in specieslist:
		TotalWeight += j.sw
	
	for i in range(stepnum):
		
		SumofR2overN = 0.
		
		for j in range(top.ns):
			#combinedenvelop[i] += psoln[i, j+top.ns]*1000/sqrt(2)*speciesI[j]/sum(speciesI)
			SumofR2overN += psolnwarp[i, j+top.ns]**2*(specieslist[j].sw/TotalWeight)
		
		combinedenvelop[i] = SumofR2overN**0.5*1000/sqrt(2)
	
	plg(combinedenvelop,sss, color="black", type="dash")	
	
	fma()
	
	
	
	## Compare Env. Model with Env. Model using WARP input
	
	# --- Target Species, x-plane 
	
	ptitles("Env. Model (solid), Env. Model with WARP input (dashed)","z [m]","RMS x-Envelope [mm]", )
	
	plg(psoln[:,20]*1000/sqrt(2),sss, color="magenta")
	plg(psoln[:,21]*1000/sqrt(2),sss, color="green")
	plg(psolnwarp[:,20]*1000/sqrt(2),sss, color="magenta", type="dash")
	plg(psolnwarp[:,21]*1000/sqrt(2),sss, color="green", type="dash")
	
	combinedenvelop = [0]*stepnum
	
	TotalWeight=0.
	for j in specieslist:
		TotalWeight += j.sw
	
	for i in range(stepnum):
		
		SumofR2overN = 0.
		
		for j in range(top.ns):
			#combinedenvelop[i] += psoln[i, j+top.ns]*1000/sqrt(2)*speciesI[j]/sum(speciesI)
			SumofR2overN += psolnwarp[i, j+top.ns]**2*(specieslist[j].sw/TotalWeight)
		
		combinedenvelop[i] = SumofR2overN**0.5*1000/sqrt(2)
	
	plg(combinedenvelop,sss, color="black", type="dash")	
	
	
	
	combinedenvelop = [0]*stepnum
	
	TotalWeight=0.
	for j in specieslist:
		TotalWeight += j.sw
	
	for i in range(stepnum):
		
		SumofR2overN = 0.
		
		for j in range(top.ns):
			#combinedenvelop[i] += psoln[i, j+top.ns]*1000/sqrt(2)*speciesI[j]/sum(speciesI)
			SumofR2overN += psoln[i, j+top.ns]**2*(specieslist[j].sw/TotalWeight)
		
		combinedenvelop[i] = SumofR2overN**0.5*1000/sqrt(2)
	
	plg(combinedenvelop,sss, color="black")	
	
	fma()


#ptitles("Fields: %s, f_neut: %s, Correction: %s, CentralDifference" %(abc, neut_f1, CorrectionMode))

#fma()