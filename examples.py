from blackjack_simulation import Simulation


print("Five 10000 round simulations with bet of 10:")
simulations = [Simulation(10000, 10) for _ in range(5)]

for i, sim in enumerate(simulations):
    print("\nSIMULATION", i + 1, ":")
    print(f"Total profit: {sim.win_amount_total}")
    print(f"Max balance during playing: {max(sim.cumulative_profit)}")
    print(f"Min balance during playing: {min(sim.cumulative_profit)}")

print("---------------------------------------------------------------------------------------------------------------")
print("How much dealer hitting on soft 17 rule hurts the player?")
print("One 100000 round simulation (bet=1) for both cases:\n")

print("Overview with standard rules:")
standard_sim = Simulation(100000, 1, False)
standard_sim.overview()

print("")
print("Overview with soft 17 rule:")
soft17_sim = Simulation(100000, 1, True)
soft17_sim.overview()

print("---------------------------------------------------------------------------------------------------------------")
print("Cumulative profit graphs for both cases:")
standard_sim.plot_profit_cumulative()
soft17_sim.plot_profit_cumulative()
