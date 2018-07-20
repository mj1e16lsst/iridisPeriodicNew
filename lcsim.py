import simulate_lc
import matplotlib.pyplot as plt

mlc = 0.0

model = 'sharp'

nn = 2880 #(86400./30.)
delt = 30.0

params = [1.0, 10**(-6), -1.0, -2.0, 0.0]

sim_lc = simulate_lc.lc_sim(nn, delt, mlc, model, params)

print(sim_lc)

plt.plot(sim_lc)
plt.show()
