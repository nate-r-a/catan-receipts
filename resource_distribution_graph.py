import plotly.plotly as py
import plotly.graph_objs as go
from plotly import __version__

# values = [37, 22, 17, 20, 13, 6] #<-- sample values
def create_graph(resources):

	all_white = ["rgb(255,255,255)","rgb(255,255,255)","rgb(255,255,255)","rgb(255,255,255)","rgb(255,255,255)"]

	# values = [37, 22, 17, 20, 13, 6] <-- example values
	resources = resources[0:-1]

	labels = ["Wood", "Sheep", "Wheat", "Brick", "Stone"]

	trace1 = go.Pie(labels=labels,values=resources,
				 marker = dict(
				 	line = dict(
				 		color = "rgb(0,0,0)",
				 		width = 3),
				 	colors = all_white),
				 textinfo = "label+value",
				 textfont = dict(size = 22,
				 				 color = "rgb(0,0,0)",
				 				 family = "Raleway"),
				 showlegend = False,
				 pull = .05
				 # rotation = randint(0,360)
				 )

	layout = go.Layout(width = 325,
					height = 325,
					margin = dict(b = 2,
								  l = 2,
								  r = 2,
								  t = 2)
					)

	fig = go.Figure(data=[trace1], layout=layout)


	# trace = go.Pie(labels=labels,values=values)

	py.image.save_as(fig, 'resources.png')


#create_graph(values)