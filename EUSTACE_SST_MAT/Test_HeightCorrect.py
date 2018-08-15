# Program to play with HeightCorrect for various different assumptions and states and make plots

# What is the sensitivity to the assumption of L?
# - if delat u/AT/SHU is small then we're ok 

# Plot 3 scenarios for each variable against L = -200 to 200.

# NOTES:
# so we really only care where the stability parameter is between -1 to 0.5, which for different zu excludes L close to zero
# There is a jump when we set 'NEUTRAL' to within little_zeta = -0.1 to 0.1, now changed to -0.01 to 0.01
# Where AT > SST increase in height = increase in T, decrease in height = decrease in T ~STABLE?
# Where AT < SST increase in height = decrease in T, decrease in height = increase in T ~UNSTABLE?
# Saturation/high humidity = increase in height = increase in q, decrease in height = decrease in q
# Low humidity = increase in height = decrease in q, decrease in height = increase in q

# Big question is how much error do we introduce/remove by bias correcting using an assumed L?
# - L assumed -50, 50, or infinity 
# - little_zeta assumed -0.4, 0.4 or 0
#--------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import HeightCorrect as hc
import CalcHums as ch # needed later to test conversion across humidity parameters
import pdb # pdb.set_trace() or c 


OutPlotT = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/Test_HeightCorrectProxyLz0_AT_a_APR2016'
OutPlotq = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/Test_HeightCorrectProxyLz0_SHU_a_APR2016'
OutPlotu = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/Test_HeightCorrectProxyLz0_U_a_APR2016'
OutDiffPlotT = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/Test_HeightCorrectProxyLz0_AT_aDIFF_APR2016'
OutDiffPlotq = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/Test_HeightCorrectProxyLz0_SHU_aDIFF_APR2016'
OutDiffPlotu = '/data/local/hadkw/HADCRUH2/MARINE/IMAGES/Test_HeightCorrectProxyLz0_U_aDIFF_APR2016'

OutDiffTextT = '/data/local/hadkw/HADCRUH2/MARINE/LISTS/Test_HeightCorrectProxyLz0_AT_aDIFF_APR2016.txt'
OutDiffTextq = '/data/local/hadkw/HADCRUH2/MARINE/LISTS/Test_HeightCorrectProxyLz0_SHU_aDIFF_APR2016.txt'
OutDiffTextu = '/data/local/hadkw/HADCRUH2/MARINE/LISTS/Test_HeightCorrectProxyLz0_U_aDIFF_APR2016.txt'

# Set up arrays to run through hc.run_heightcorrect_proxyLz0(): Lmin, Lmax, sst, at, shu, u, q, zu, zt, zq

# Set up Lmin_arr and Lmax_arr
# If stability parameter (little_zeta) cannot be less than -1 or greater than 0.5 over ocean then this restricts L: 
# e.g. for zu = 20m:
# 	-200 to -20 (anything < -200 = 'NEUTRAL' e.g. -0.1 < little_zeta < 0
# 	40 to 200 (anything > 200 = 'NEUTRAL' e.g. 0 < little_zeta < 0.1
Lmin_arr = np.arange(-250,0,1) # avoids ridiculously UNSTABLE conditions but includes near-NEUTRAL conditions (at least by our definition of little_zeta between -0.1 and 0.1
Lmax_arr = np.arange(1,251,1) 	 # avoids ridiculously STABLE conditions but includes near-NEUTRAL conditions
Lfix_arr = np.append(Lmin_arr,Lmax_arr)
sst_arr = [-1.,0.,10.,20.,30.]
at_arr = [-30., -15., 0., 15., 30.]
shu_arr = [1., 10., 20.]
u_arr = [0.5, 1., 5., 10.,20.,]
zu = [5., 10., 20., 30.]
zt = [4., 8., 16., 24.]
zq = [4., 8., 16., 24.]

# create unlikely flags to note those combinations that are not really physically possible
unlikely_t = ['','','*','*','*','','','*','*','*','','','','*','*','*','*','','','*','*','*','','','']
unlikely_q = ['','','','*','*','*','*','','','*','*','*','*','','']

# Now build a plot for AT, SHU and U to show variation
gap= 0.03
cols = ['grey','red','gold','blue','violet','grey','red','gold','blue','violet','grey','red','gold','blue','violet','grey','red','gold','blue','violet','grey','red','gold','blue','violet']
lins = ['-','-','-','-','-','-','-','-','-','-','--','--','--','--','--',':',':',':',':',':','-.','-.','-.','-.','-.']
linsfat = [1,1,1,1,1,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
linstext = ['thin-solid','thin-solid','thin-solid','thin-solid','thin-solid','wide-solid','wide-solid','wide-solid','wide-solid','wide-solid','dashed','dashed','dashed','dashed','dashed','dotted','dotted','dotted','dotted','dotted','dotdash','dotdash','dotdash','dotdash','dotdash']

# Loop through the range of sst, at, shu, u, zu, zt/zq to get values for each L
# 25 lines for each height, for each sst/at, sst/shu, 5 lines for u
for h,hh in enumerate(zu): # loop through the five heights
    little_zeta_arr = hh/Lfix_arr 
    low_lil_z = np.where(abs(little_zeta_arr - (-0.5)) == min(abs(little_zeta_arr - (-0.5))))[0]
    high_lil_z = np.where(abs(little_zeta_arr - 0.25) == min(abs(little_zeta_arr - 0.25)))[0]
    gots = np.where((little_zeta_arr > -1) & (little_zeta_arr < 0.5))[0]
    print(little_zeta_arr[low_lil_z],little_zeta_arr[high_lil_z])
# Temperature focus - doesn't matter what q is doing 
# does still use u* for L but we're not calculating L
# also requires momentum related PHI and Y but these only use little_zeta and zu
    resultT = np.zeros((25,len(Lfix_arr)))
    diffT = np.zeros((25,len(Lfix_arr)))
    # range for minimum(permitted) diff, little_zeta=-0.5 diff, little_zeta=0.25 diff, maximum(permitted) diff, resolved diff, resolved actual, resolved L
    rangeT = np.zeros((25,7)) 
    for t,tt in enumerate(at_arr):
        for s, ss in enumerate(sst_arr):
	    for l,ll in enumerate(Lfix_arr):
                # 5 * 5 = 25
	        u10,at10,shu10 = hc.run_heightcorrect_proxyLz0(ss,tt,8.,5.,hh,zt[h],zq[h],Lfix = ll)
		resultT[(t*5)+s,l] = at10
		diffT[(t*5)+s,l] = at10 - tt
	    rangeT[(t*5)+s,0] = min(diffT[(t*5)+s,gots])
	    rangeT[(t*5)+s,1] = diffT[(t*5)+s,low_lil_z]
	    rangeT[(t*5)+s,2] = diffT[(t*5)+s,high_lil_z]
	    rangeT[(t*5)+s,3] = max(diffT[(t*5)+s,gots])
	    adjdict,heightdict = hc.run_heightcorrection_final(ss,tt,8.,5.,hh,zt[h],zq[h])
	    rangeT[(t*5)+s,4] = adjdict['at_10m'] - tt
	    rangeT[(t*5)+s,5] = adjdict['at_10m']
	    rangeT[(t*5)+s,6] = heightdict['L']	    
#	    pdb.set_trace()
	    
# specific humidity focus - does matter what sst is doing, doesn't matter what at is doing unless we have Lmin and Lmax as we need the SST-AT difference
# does still use u* for L but we're not calculating L
# also requires momentum related PHI and Y but these only use little_zeta and zu
    resultq = np.zeros((15,len(Lfix_arr)))
    diffq = np.zeros((15,len(Lfix_arr)))
    # range for minimum(permitted) diff, little_zeta=-0.5 diff, little_zeta=0.25 diff, maximum(permitted) diff, resolved diff, resolved actual, resolved L
    rangeq = np.zeros((15,7)) 
    for q, qq in enumerate(shu_arr):
        for s, ss in enumerate(sst_arr):
	    for l,ll in enumerate(Lfix_arr):
		# 5 * 3 = 15
	        u10,at10,shu10 = hc.run_heightcorrect_proxyLz0(ss,10.,qq,5.,hh,zt[h],zq[h],Lfix = ll)
		resultq[(q*5)+s,l] = shu10
		diffq[(q*5)+s,l] = shu10 - qq
	    rangeq[(q*5)+s,0] = min(diffq[(q*5)+s,gots])
	    rangeq[(q*5)+s,1] = diffq[(q*5)+s,low_lil_z]
	    rangeq[(q*5)+s,2] = diffq[(q*5)+s,high_lil_z]
	    rangeq[(q*5)+s,3] = max(diffq[(q*5)+s,gots])
	    adjdict,heightdict = hc.run_heightcorrection_final(ss,10.,qq,5.,hh,zt[h],zq[h])
	    rangeq[(q*5)+s,4] = adjdict['shu_10m'] - qq
	    rangeq[(q*5)+s,5] = adjdict['shu_10m']
	    rangeq[(q*5)+s,6] = heightdict['L']	  

# wind focus - doesn't matter what at and sst is doing unless we have Lmin and Lmax as we need the SST-AT difference
# doesn't matter what q is doing
    resultu = np.zeros((5,len(Lfix_arr)))
    diffu = np.zeros((5,len(Lfix_arr)))
    # range for minimum(permitted) diff, little_zeta=-0.5 diff, little_zeta=0.25 diff, maximum(permitted) diff, resolved diff, resolved actual, resolved L
    rangeu = np.zeros((5,7)) 
    for u, uu in enumerate(u_arr):
        for l,ll in enumerate(Lfix_arr):
	    # 5 = 5
	    u10,at10,shu10 = hc.run_heightcorrect_proxyLz0(5.,10.,8.,uu,hh,zt[h],zq[h],Lfix = ll)
	    resultu[u,l] = u10
	    diffu[u,l] = u10 - uu
	    rangeu[u,0] = min(diffu[u,gots])
	    rangeu[u,1] = diffu[u,low_lil_z]
	    rangeu[u,2] = diffu[u,high_lil_z]
	    rangeu[u,3] = max(diffu[u,gots])

    plt.clf()
    fig, ax1 = plt.subplots()
    countT = 0
    countS = 0
    for i in range(25):
        ax1.plot(Lfix_arr,resultT[i,:],c=cols[i],linestyle=lins[i],linewidth=linsfat[i])
	if (rangeT[i,6] < -250):
	    Lplot = -250
	elif (rangeT[i,6] > 250):
	    Lplot = 250
	else:
	    Lplot = rangeT[i,6]    
#	print(Lplot,rangeT[i,6],rangeT[i,5])
	if (unlikely_t[i] == '*'):
	    ax1.plot(Lplot,rangeT[i,5],c=cols[i],linestyle='',marker='x',mew=3, ms=10) # markeredgewidth and markersize
	else:
	    ax1.plot(Lplot,rangeT[i,5],c=cols[i],linestyle='',marker='o')
        ax1.annotate(unlikely_t[i]+"T="+"{:3d}".format(int(at_arr[countT]))+",SST="+"{:3d}".format(int(sst_arr[countS]))+","+linstext[i],xy=(0.75,0.94-(i*gap)),xycoords='axes fraction',size=8,color=cols[i])
        countS = countS+1
        if (countS == 5):
            countT = countT+1
	    countS = 0
    ax1.set_ylim(min(at_arr)-5.,max(at_arr)+5)	
    ax1.set_xlim(min(Lfix_arr)-20.,max(Lfix_arr)+200)	
    # fill where stability parameter is < -1 and > 0.5 sp = zu[x]/Lfix_arr[x] therefore L = zu[x]/sp
    ax1.fill([zu[h]/-1.,zu[h]/0.5,zu[h]/0.5,zu[h]/-1.],[min(at_arr)-5,min(at_arr)-5,max(at_arr)+5,max(at_arr)+5], facecolor='grey')
    ax1.set_xlabel('L (Monin-Obukhov length) (m)')
    ax1.set_ylabel('Temperature (degrees C)', color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-250.),xy=(-250,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-200.),xy=(-200,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-150.),xy=(-150,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-100.),xy=(-100,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-50.),xy=(-50,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/50.),xy=(50,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/100.),xy=(100,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/150.),xy=(150,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/200.),xy=(200,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/250.),xy=(250,min(at_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.plot([-250,-200,-150,-100,-50,50,100,150,200,250],np.repeat(min(at_arr)-4.,10),marker = 'o',linestyle = '', color = 'black')
    plt.tight_layout()

    #plt.savefig(OutPlotT+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".eps")
    plt.savefig(OutPlotT+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".png")
    plt.close()

    plt.clf()
    fig, ax1 = plt.subplots()
    countT = 0
    countS = 0
    for i in range(25):
        ax1.plot(Lfix_arr,diffT[i,:],c=cols[i],linestyle=lins[i],linewidth=linsfat[i])
	if (rangeT[i,6] < -250):
	    Lplot = -250
	elif (rangeT[i,6] > 250):
	    Lplot = 250
	else:
	    Lplot = rangeT[i,6]    
#	print(Lplot,rangeT[i,6],rangeT[i,4])
	if (unlikely_t[i] == '*'):
	    ax1.plot(Lplot,rangeT[i,4],c=cols[i],linestyle='',marker='x',mew=3, ms=10)
        else:
	    ax1.plot(Lplot,rangeT[i,4],c=cols[i],linestyle='',marker='o')
	ax1.annotate(unlikely_t[i]+"T="+"{:3d}".format(int(at_arr[countT]))+",SST="+"{:3d}".format(int(sst_arr[countS]))+","+linstext[i],xy=(0.75,0.94-(i*gap)),xycoords='axes fraction',size=8,color=cols[i])
        countS = countS+1
        if (countS == 5):
            countT = countT+1
	    countS = 0
    ax1.set_ylim(-10,10)	
    ax1.set_xlim(min(Lfix_arr)-20.,max(Lfix_arr)+200)	
    # fill where stability parameter is < -1 and > 0.5 sp = zu[x]/Lfix_arr[x] therefore L = zu[x]/sp
    ax1.fill([zu[h]/-1.,zu[h]/0.5,zu[h]/0.5,zu[h]/-1.],[-10,-10,10,10], facecolor='grey')
    ax1.set_xlabel('L (Monin-Obukhov length) (m)')
    ax1.set_ylabel('Adjusted - Observed Temperature (degrees C)', color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-250.),xy=(-250,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-200.),xy=(-200,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-150.),xy=(-150,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-100.),xy=(-100,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-50.),xy=(-50,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/50.),xy=(50,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/100.),xy=(100,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/150.),xy=(150,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/200.),xy=(200,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/250.),xy=(250,-9.5),xycoords='data',ha='center',size=12,color='black')
    ax1.plot([-250,-200,-150,-100,-50,50,100,150,200,250],np.repeat(-9.9,10),marker = 'o',linestyle = '', color = 'black')
    plt.tight_layout()

    #plt.savefig(OutDiffPlotT+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".eps")
    plt.savefig(OutDiffPlotT+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".png")
    plt.close()

    # Write out stats to file (append!)
    #pdb.set_trace()
    filee=open(OutDiffTextT,'a+')
    countT = 0
    countS = 0
    for i in range(25):
#        print(rangeT[i,0])
#        print(rangeT[i,1])
#        print(rangeT[i,2])
#        print(rangeT[i,3])
        filee.write(str('Zu: '+"{:2d}".format(int(hh))+\
                        'Zt: '+"{:2d}".format(int(zt[h]))+\
		        '{:2s}'.format(unlikely_t[i])+\
		        '  AT: '+"{:6.2f}".format(at_arr[countT])+\
		        ' SST: '+"{:6.2f}".format(sst_arr[countS])+\
		        ' MIN: '+"{:6.2f}".format(rangeT[i,0])+\
		        ' MNU: '+"{:6.2f}".format(rangeT[i,1])+\
		        ' MNS: '+"{:6.2f}".format(rangeT[i,2])+\
		        ' MAX: '+"{:6.2f}".format(rangeT[i,3])+\
		        ' RES: '+"{:6.2f}".format(rangeT[i,4])+\
		        '   L: '+"{:6.2f}".format(rangeT[i,6])+\
		        '\n'))
        countS = countS+1
        if (countS == 5):
            countT = countT+1
	    countS = 0

    filee.close()

    plt.clf()
    fig, ax1 = plt.subplots()
    countq = 0
    countS = 0
    for i in range(15):
        ax1.plot(Lfix_arr,resultq[i,:],c=cols[i],linestyle=lins[i],linewidth=linsfat[i])
	if (rangeq[i,6] < -250):
	    Lplot = -250
	elif (rangeq[i,6] > 250):
	    Lplot = 250
	else:
	    Lplot = rangeq[i,6]    
#	print(Lplot,rangeq[i,6],rangeq[i,4])
	if (unlikely_q[i] == '*'):
	    ax1.plot(Lplot,rangeq[i,5],c=cols[i],linestyle='',marker='x',mew=3, ms=10)
	else:
	    ax1.plot(Lplot,rangeq[i,5],c=cols[i],linestyle='',marker='o')
        ax1.annotate(unlikely_q[i]+"q="+"{:3d}".format(int(shu_arr[countq]))+",SST="+"{:3d}".format(int(sst_arr[countS]))+","+linstext[i],xy=(0.75,0.94-(i*gap)),xycoords='axes fraction',size=8,color=cols[i])
        countS = countS+1
        if (countS == 5):
            countq = countq+1
	    countS = 0
    ax1.set_ylim(min(shu_arr)-5.,max(shu_arr)+5)	
    ax1.set_xlim(min(Lfix_arr)-20.,max(Lfix_arr)+200)	
    ax1.fill([zu[h]/-1.,zu[h]/0.5,zu[h]/0.5,zu[h]/-1.],[min(shu_arr)-5,min(shu_arr)-5,max(shu_arr)+5,max(shu_arr)+5], facecolor='grey')
    ax1.set_xlabel('L (Monin-Obukhov length) (m)')
    ax1.set_ylabel('Specific Humidity (g/kg)', color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-250.),xy=(-250,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-200.),xy=(-200,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-150.),xy=(-150,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-100.),xy=(-100,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-50.),xy=(-50,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/50.),xy=(50,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/100.),xy=(100,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/150.),xy=(150,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/200.),xy=(200,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/250.),xy=(250,min(shu_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.plot([-250,-200,-150,-100,-50,50,100,150,200,250],np.repeat(min(shu_arr)-4.,10),marker = 'o',linestyle = '', color = 'black')
    plt.tight_layout()

    #plt.savefig(OutPlotq+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".eps")
    plt.savefig(OutPlotq+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".png")
    plt.close()

    plt.clf()
    fig, ax1 = plt.subplots()
    countq = 0
    countS = 0
    for i in range(15):
        ax1.plot(Lfix_arr,diffq[i,:],c=cols[i],linestyle=lins[i],linewidth=linsfat[i])
	if (rangeq[i,6] < -250):
	    Lplot = -250
	elif (rangeq[i,6] > 250):
	    Lplot = 250
	else:
	    Lplot = rangeq[i,6]    
#	print(Lplot,rangeq[i,6],rangeq[i,4])
	if (unlikely_q[i] == '*'):
	    ax1.plot(Lplot,rangeq[i,4],c=cols[i],linestyle='',marker='x',mew=3, ms=10)
	else:
	    ax1.plot(Lplot,rangeq[i,4],c=cols[i],linestyle='',marker='o')
        ax1.annotate(unlikely_q[i]+"q="+"{:3d}".format(int(shu_arr[countq]))+",SST="+"{:3d}".format(int(sst_arr[countS]))+","+linstext[i],xy=(0.75,0.94-(i*gap)),xycoords='axes fraction',size=8,color=cols[i])
        countS = countS+1
        if (countS == 5):
            countq = countq+1
	    countS = 0
    ax1.set_ylim(-5,5)	
    ax1.set_xlim(min(Lfix_arr)-20.,max(Lfix_arr)+200)	
    ax1.fill([zu[h]/-1.,zu[h]/0.5,zu[h]/0.5,zu[h]/-1.],[-5,-5,5,5], facecolor='grey')
    ax1.set_xlabel('L (Monin-Obukhov length) (m)')
    ax1.set_ylabel('Adjusted - Observed Specific Humidity (g/kg)', color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-250.),xy=(-250,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-200.),xy=(-200,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-150.),xy=(-150,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-100.),xy=(-100,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-50.),xy=(-50,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/50.),xy=(50,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/100.),xy=(100,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/150.),xy=(150,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/200.),xy=(200,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/250.),xy=(250,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.plot([-250,-200,-150,-100,-50,50,100,150,200,250],np.repeat(-4.9,10),marker = 'o',linestyle = '', color = 'black')
    plt.tight_layout()

    #plt.savefig(OutDiffPlotq+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".eps")
    plt.savefig(OutDiffPlotq+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".png")

    plt.close()

    # Write out stats to file (append!)
    filee=open(OutDiffTextq,'a+')
    countq = 0
    countS = 0
    for i in range(15):
        filee.write(str('Zu: '+'{:2d}'.format(int(hh))+\
                        'Zq: '+'{:2d}'.format(int(zq[h]))+\
		        '{:2s}'.format(unlikely_q[i])+\
		        ' SHU: '+'{:6.2f}'.format(shu_arr[countq])+\
		        ' SST: '+'{:6.2f}'.format(sst_arr[countS])+\
		        ' MIN: '+'{:6.2f}'.format(rangeq[i,0])+\
		        ' MNU: '+'{:6.2f}'.format(rangeq[i,1])+\
		        ' MNS: '+'{:6.2f}'.format(rangeq[i,2])+\
		        ' MAX: '+'{:6.2f}'.format(rangeq[i,3])+\
		        ' RES: '+"{:6.2f}".format(rangeq[i,4])+\
		        '   L: '+"{:6.2f}".format(rangeq[i,6])+\
		        '\n'))
        countS = countS+1
        if (countS == 5):
            countq = countq+1
	    countS = 0

    filee.close()



    plt.clf()
    fig, ax1 = plt.subplots()
    countu = 0
    for i in range(5):
        ax1.plot(Lfix_arr,resultu[i,:],c=cols[i],linestyle=lins[i],linewidth=linsfat[i])
        ax1.annotate("U="+"{:3d}".format(int(u_arr[countu]))+linstext[i],xy=(0.75,0.94-(i*gap)),xycoords='axes fraction',size=8,color=cols[i])
        countu = countu+1
    ax1.set_ylim(min(u_arr)-5.,max(shu_arr)+5)	
    ax1.set_xlim(min(Lfix_arr)-20.,max(Lfix_arr)+200)	
    ax1.fill([zu[h]/-1.,zu[h]/0.5,zu[h]/0.5,zu[h]/-1.],[min(u_arr)-5,min(u_arr)-5,max(u_arr)+5,max(u_arr)+5], facecolor='grey')
    ax1.set_xlabel('L (Monin-Obukhov length) (m)')
    ax1.set_ylabel('Wind Speed (m/s)', color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-250.),xy=(-250,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-200.),xy=(-200,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-150.),xy=(-150,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-100.),xy=(-100,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-50.),xy=(-50,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/50.),xy=(50,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/100.),xy=(100,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/150.),xy=(150,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/200.),xy=(200,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/250.),xy=(250,min(u_arr)-3.),xycoords='data',ha='center',size=12,color='black')
    ax1.plot([-250,-200,-150,-100,-50,50,100,150,200,250],np.repeat(min(u_arr)-4.,10),marker = 'o',linestyle = '', color = 'black')
    plt.tight_layout()

    #plt.savefig(OutPlotu+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".eps")
    plt.savefig(OutPlotu+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".png")
    plt.close()

    plt.clf()
    fig, ax1 = plt.subplots()
    countu = 0
    for i in range(5):
        ax1.plot(Lfix_arr,diffu[i,:],c=cols[i],linestyle=lins[i],linewidth=linsfat[i])
        ax1.annotate("U="+"{:3d}".format(int(u_arr[countu]))+linstext[i],xy=(0.75,0.94-(i*gap)),xycoords='axes fraction',size=8,color=cols[i])
        countu = countu+1
    ax1.set_ylim(-5,5)	
    ax1.set_xlim(min(Lfix_arr)-20.,max(Lfix_arr)+200)	
    ax1.fill([zu[h]/-1.,zu[h]/0.5,zu[h]/0.5,zu[h]/-1.],[-5,-5,5,5], facecolor='grey')
    ax1.set_xlabel('L (Monin-Obukhov length) (m)')
    ax1.set_ylabel('Adjusted - Observed Wind Speed (m/s)', color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-250.),xy=(-250,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-200.),xy=(-200,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-150.),xy=(-150,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-100.),xy=(-100,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/-50.),xy=(-50,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/50.),xy=(50,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/100.),xy=(100,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/150.),xy=(150,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/200.),xy=(200,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.annotate("{:6.2f}".format(zu[h]/250.),xy=(250,-4.75),xycoords='data',ha='center',size=12,color='black')
    ax1.plot([-250,-200,-150,-100,-50,50,100,150,200,250],np.repeat(-4.9,10),marker = 'o',linestyle = '', color = 'black')
    plt.tight_layout()

    #plt.savefig(OutDiffPlotu+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".eps")
    plt.savefig(OutDiffPlotu+"_"+"{:d}".format(int(hh))+"_"+"{:d}".format(int(zt[h]))+".png")
    plt.close()
 
    # Write out stats to file (append!)
    filee=open(OutDiffTextu,'a+')
    countu = 0
    for i in range(5):
        filee.write(str('Zu: '+'{:2d}'.format(int(hh))+\
		        '   U: '+'{:6.2f}'.format(u_arr[countu])+\
		        ' MIN: '+'{:6.2f}'.format(rangeu[i,0])+\
		        ' MNU: '+'{:6.2f}'.format(rangeu[i,1])+\
		        ' MNS: '+'{:6.2f}'.format(rangeu[i,2])+\
		        ' MAX: '+'{:6.2f}'.format(rangeu[i,3])+\
		    '\n'))
        countu = countu+1

    filee.close()
