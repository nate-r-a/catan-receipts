import plotly.plotly as py
from plotly.graph_objs import Bar, Scatter, Figure, Layout
from plotly import __version__

def create_graph(actual_rolls):
	#x-axis
	NUMBERS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
	#relative odds of a number being rolled
	ODDS = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]

	#calculate expected rolls
	expected_rolls = []
	total = 0
	for i in actual_rolls:
		total += i
	for i in ODDS:
		expected_rolls.append((total/36) * i)

	#Sample values for testing
	#y-axis - bar
	#actual_rolls = [0, 5, 2, 5, 4, 3, 8, 9, 1, 1, 2]
	#y-axis - scatter
	#expected_rolls = [1.1111111111111112, 2.2222222222222223, 3.3333333333333335, 4.444444444444445, 5.555555555555555, 6.666666666666667, 5.555555555555555, 4.444444444444445, 3.3333333333333335, 2.2222222222222223, 1.1111111111111112]


	trace1 = Bar(x=NUMBERS,y=actual_rolls,
				 name = "Actual",
				 marker = dict(
				 	line = dict(
				 		color = "rgb(0,0,0)",
				 		width = 5),
				 	color = "rgb(255,255,255)")
				 )


	trace2 = Scatter(x=NUMBERS, y=expected_rolls,
					 name = "Expected",
					 marker = dict(
					 	size = 10,
					 	color = "rgb(0,0,0)",
					 	symbol = "hexagon"
					 	)
					 )

	data = [trace1, trace2]

	layout = Layout(width = 365,
					height = 310,
					xaxis = dict(autotick = False,
								 tick0 = 2,
								 dtick = 1,
								 tickfont = dict(size = 18)),
					yaxis = dict(tickfont = dict(size = 18)),
					margin = dict(b = 25,
								  l = 25,
								  r = 0,
								  t = 0),
					showlegend = False)


	fig = Figure(data=data,layout=layout)

	# Save the figure as a png image:
	py.image.save_as(fig, 'dice_rolls.png')

	
#Sample rolls for testing
# actual_rolls = [0, 5, 2, 5, 4, 3, 8, 9, 1, 1, 2]
# expected_rolls = [1.1111111111111112, 2.2222222222222223, 3.3333333333333335, 4.444444444444445, 5.555555555555555, 6.666666666666667, 5.555555555555555, 4.444444444444445, 3.3333333333333335, 2.2222222222222223, 1.1111111111111112]
#create_graph(actual_rolls)

# trace1 = go.Scatter(
#     x=NUMBERS,
#     y=expected_rolls
# )
# trace2 = go.Bar(
#     x=NUMBERS,
#     y=actual_rolls
# )

# data = [trace1, trace2]
# py.plot(data, filename='bar-line')