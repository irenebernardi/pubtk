from pubtk.runtk import NetpyneRunner

main = NetpyneRunner()

cfg = main.get_cfg()

cfg.duration = 1*1e3        # Duration of the simulation, in ms
cfg.dt = 0.025              # Internal integration timestep to use
cfg.verbose = False         # Show detailed messages
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStep = 0.1        # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = 'tut8'       # Set file output name
cfg.saveJson = True
cfg.printPopAvgRates = True
cfg.analysis['plotRaster'] = {'saveFig': True}                   # Plot a raster
cfg.analysis['plotTraces'] = {'include': [0], 'saveFig': True}  # Plot recorded traces for this list of cells

cfg.saveDataInclude = ['simData', 'simConfig', 'netParams', 'net']

# Variable parameters (used in netParams)
cfg.synMechTau2 = 5
cfg.connWeight = 0.01

# network parameters
cfg.send = None
main.set_mappings('cfg')
