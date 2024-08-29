from qel_simulation import Simulation
from data.sim_config import config
qsim = Simulation(name=f"Example_Inventory_Management", config=config)
qsim.start_simulation()
qsim.export_simulated_log()
