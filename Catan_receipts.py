import webbrowser, os, re
from PIL import Image

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import resource_distribution_graph as resgraph
import roll_graph as rollgraph

#print("Starting...")
gameID = 67 #input("Game ID: ")

#Checks to see if the file has already been made
filename = "catan_receipt_game_{number}.html".format(number=gameID)
bitmap_filename = filename[:-5]+".bmp"
print(filename)
if os.path.isfile(filename):
	print("File has already been made")
	quit()
else:
	print("Creating file...")

#Sets where most of a game's data can be found
input_row = str(gameID + 1)
summary_row = str(gameID + 4)


#Google API credentials
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('[Your Google API json file here]', scope)
gc = gspread.authorize(credentials)

#Opens the workbook
wb = gc.open("FoC RS v2.0 SUPER ALPHA")

#Shortcuts to open the corresponding tabs
input_sheet = wb.worksheet("Input")
summary_sheet = wb.worksheet("Summary")
scratch_sheet = wb.worksheet("Scratch")
timeline_sheet = wb.worksheet("Timeline")

#The HTML document -- I am fully aware I used <br>'s in a very silly way
html_content = """
<!DOCTYPE html>
<html class="html">

<head>
	<link rel="stylesheet" href="css/main.css">
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<link href="https://fonts.googleapis.com/css?family=Archivo+Black" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css?family=Archivo+Narrow" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css?family=Raleway:400,500,700,900" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css?family=Rubik:400,500,700,900" rel="stylesheet">
	<title>Catan Receipts</title>
</head>
<body>
	<div class="receipt">
	<br>

		<div class="title-container">
			<p class="title">F E D E R A T I O N</p>
			<p class="title-bottom">C A T A N</p>
		</div>
		<br>
		<br>
		<br>
		<!--repeat for # of players-->
		<div class="game-number-container"> 
			{number_and_date}
			<p class="underline"></p>
			
		</div>
		<br>

<!--To be repeated for each player-->
<!--Game scores-->
		{player_scores}		

<!--End player scores/ratings-->
		<!--Collusion-->
		<div class="collusion">
			<img src="collusion.png" class="collusion-sign">
			<div class="collusion-text">
			Warning! High levels of collusion detected!
			</div>
		</div>


		<br>

		<div class="subtitle">
			Dice Rolls
		</div>
		<div class="dice-rolls">
			<p class="roll-list">{roll_list}</p>
			<div class="dice-roll-chart">
				<img src="dice_rolls.png">
			</div>
		</div>
		<br>

		<div class="subtitle">
			Resource Availability
		</div>
		<div class="resource-availability">
			<div class="resource-locations">
				<p class="locations">
					{resource_availability}
				</p>
			</div>
		</div>
		<div class="resources-chart">
				<img src="resources.png">
		</div>
		<br>

		<div class="subtitle">
			Leaderboard <br class="leaderboard-date">(as of {date})
		</div>
		<!--leaderboard-->
		{leaderboard_panel}		

	<br>

			

	</div>
</body>
</html>
"""

#############################################

#Pulls the game # and date (date is global for use in leaderboard later)
date = input_sheet.acell("C"+input_row).value
number_and_date = '''<p class="game-number">Game {game_number} - {date}</p>'''

def create_number_and_date(gameID):
	content = ""
	content = number_and_date.format(game_number = gameID, date = date)
	return content



#There is always collusion
collusion = """
		<div class="collusion">
			<img src="more catan scripts/collusion.png" class="collusion-sign">
			Warning! High levels of collusion detected!
		</div>
		"""


player_score_panel = """
		<div class="player-score-container">
			<div class="player-name">{Player}</div>
			<div class="player-score">{Score}</div>
		</div>
		<div class="player-rating">
			{Old} <img src="arrow.png" class="arrow"> {New} ({Change})
		</div>
		<br>
		"""

def create_player_score_panels():
	content = ""

	#Pulls all cells in range, then effectively removes empty cells
	score_range = input_sheet.range("F"+input_row+":Q"+input_row)
	raw_value_list = [cell.value for cell in score_range if cell.value != ""]

	#Players and scores are located in alternating cells
	player_list = raw_value_list[::2]
	score_list = raw_value_list[1::2]

	#Similar to the score_range creation, but pulling from a different set of cells
	rating_range = summary_sheet.range("F"+summary_row+":AC"+summary_row)
	raw_rating_list = [cell.value for cell in rating_range if cell.value != ""]

	#Each player has 4 cells, one each for name, score, old rating, and new rating --
	#This iterates over all pulled cells and separates them by player
	rating_list = [list(z) for z in zip(raw_rating_list[::4], raw_rating_list[1::4],
									 raw_rating_list[2::4], raw_rating_list[3::4])]

	for player in rating_list:
		#Finds players who have "(Prov)" after their ratings, and takes that part out:
		try:
			int(player[2])
		except ValueError:
			player[2] = player[2][:-8]

		try:
			int(player[3])
		except ValueError:
			player[3] = player[3][:-8]

		#Adds a change in rating element to each player's list
		player.append(str(int(player[3])-int(player[2])))
		if player[4] == 0:
			player[4] = "0"
		if int(player[4]) > 0:
			player[4] = "+" + player[4]

		content += player_score_panel.format(Player = player[0],
											 Score = player[1],
											 Old = player[2],
											 New = player[3],
											 Change = player[4])
	return content

def create_dice_roll_list():
	#Pulls the dice roll cell, all in one string
	cell = ""
	cell = "R" + str(gameID+1)

	#Selects the corresponding dice roll cell (given as string)
	dice_rolls = input_sheet.acell(cell).value

	return dice_rolls

#Creates a global variable for use in a few different places when needed
dice_rolls = create_dice_roll_list()

resource_location_panel = """
				<p class="locations">{resource_locations}</p>
				"""

def create_resource_panel():
	#This takes the dice roll and resource locations, and creates the 
	#two graphs for the receipt and creates other bits of data
	content = ""
	resources = ["Wood", "Sheep", "Wheat", "Brick", "Stone", "Desert"]
	resource_list = ["wo", "sh", "wh", "br", "st", "de"]

	#converts the dice_rolls string to a list (of strings)
	roll_list = dice_rolls.split()
	#converts those strings to ints
	rolls = [int(i) for i in roll_list]
	#creates roll distribution list and fills it with roll counts
	roll_distr = []
	for n in range(11):
		n_count = rolls.count(n+2)
		roll_distr.append(n_count)
	print(roll_distr)

	#gets the board layout, follows similar steps to
	#the creation of roll_distr
	cell = "S" + str(gameID+1)
	layout = input_sheet.acell(cell).value
	board_tiles = layout.split()
	print(board_tiles)
	
	#number layout for 3-4 player game
	NUMBER_TILES = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
	#number layout for 5-6 player game
	if len(board_tiles) > 19:
		NUMBER_TILES = [2, 5, 4, 6, 3, 9, 8, 11, 11, 10, 6, 3, 8, 4, 8, 
					10, 11, 12, 10, 5, 4, 9, 5, 9, 12, 3, 2, 6]

	#adds 7s in positions where desert spots are
	de_indices = [i for i, x in enumerate(board_tiles) if x == "de"]
	for i in de_indices:
		NUMBER_TILES.insert(i,7)


	#Gathers how many times each resource was "rolled" (does not include deserts)
	resource_positions_list = []
	wood_count, sheep_count, wheat_count, brick_count, stone_count, desert_count = 0,0,0,0,0,0
	resource_count_list = [wood_count, sheep_count, wheat_count, 
					   brick_count, stone_count, desert_count]

	for idx in range(6):
		print("index", idx, resources[idx])
		#finds indices of land tiles in board_tiles list (corresponds to a # on NUMBER_TILES)
		resource_positions = [i for i, x in enumerate(board_tiles) if x == resource_list[idx]]
		print(resource_positions)
		resource_positions_list.append(resource_positions)
		

		#Takes the value at resource_positions[r] (which is a possible dice roll),
		#multiplies it by the number of times it was rolled, and
		#adds it to the count for the corresponding resource
		for r in range(len(resource_positions)):
			#print("r index =", r)
			print("position: ",resource_positions[r])
			print("roll on that space: ",NUMBER_TILES[resource_positions[r]])
			print("times that was rolled: ",roll_distr[NUMBER_TILES[resource_positions[r]]-2])
			resource_count_list[idx] += roll_distr[NUMBER_TILES[resource_positions[r]]-2]
			print(resource_count_list[idx])

	#Creates pie chart:
	resgraph.create_graph(resource_count_list)	
	#Creates roll graph:
	rollgraph.create_graph(roll_distr)
	

	#Makes a nice list of what numbers the resources are on
	#There is almost certainly a better way to do this -- will combine indices
	resource_index = 0
	resource_text = []
	for position_list in resource_positions_list[:-1]:
		spots = []
		for position in position_list:
			spots.append(NUMBER_TILES[position]) 

		spots = list(set(spots))
		spots = sorted(spots)
		last = str(spots[-1])

		spot_string = ", ".join(str(x) for x in spots[:-1])

		#Removes Oxford comma when a resource is on only 1 or 2 numbers
		if len(spots) == 2:
			resource_text.append(resources[resource_index]+ " on " + str(spots[0]) + " and "+ last)
		else:
			resource_text.append(resources[resource_index]+ " on " + spot_string +", and "+ last)

		resource_index += 1

	for locations in resource_text:
		content += resource_location_panel.format(resource_locations = locations)

	return content
		

leaderboard_panel = """
		<div class="player-score-container leaderboard">
			<div class="leader-name">{num_Player}</div>
			<div class="leader-score">{Rating}</div>
		</div>
		"""


def create_leaderboard_panel():
	#Needs a bit of editing to get it to work with games before 8/8/16
	content = ""

	#Trims year off
	print(date[:-3])
	column = timeline_sheet.find(str(date[:-3]))
	column = column.col
	#print(column)

	#Finds range of top 5 players in sheet for use in next step
	top_player = timeline_sheet.get_addr_int(17,column)
	fifth_player = timeline_sheet.get_addr_int(21,column)
	#print(top_player)
	leader_range = timeline_sheet.range(top_player + ":" + fifth_player)
	#print(leader_range)

	#Makes list of top 5 players
	leader_list = []
	leader_ratings = []
	for i in range(5):
		name = scratch_sheet.findall(leader_range[i].value)[-2].value
		leader_list.append(name)
		leader_list[i] = str(i+1) + ". " + leader_list[i]
		row = scratch_sheet.findall(leader_range[i].value)[-2].row
		# print(row)
		rating = scratch_sheet.cell(row,column).value
		leader_ratings.append(rating)

	for i in range(5):
		content += leaderboard_panel.format(num_Player = leader_list[i],
											Rating = leader_ratings[i])


	# print(content)
	return content
	# print(leader_list)
	# print(leader_ratings)

#Formats above HTML code to include all steps above
new_page = html_content.format(number_and_date = create_number_and_date(gameID),
					player_scores = create_player_score_panels(),
					roll_list = dice_rolls,
					resource_availability = create_resource_panel(),
					date = date,
					leaderboard_panel = create_leaderboard_panel())

# print(new_page)

# Creates or overwrite the output file
# filename = "catan_receipt_game_{number}.html".format(number=gameID)
output_file = open(filename, 'w', encoding="utf-8")

# Outputs the file
output_file.write(new_page)
output_file.close()

#Runs wkhtmltoimage, creating a bitmap pf the page
cmd = "wkhtmltoimage --crop-w 384 --crop-x 8 --crop-y 48 --quality 0" + " " + filename + " " + bitmap_filename
print(cmd)
os.system(cmd)
#Rotates the bitmap 180 degrees, converts to 1-bit BMP (for better printing)
bmp = Image.open(bitmap_filename)
bmp2 = bmp.rotate(180)
gray = bmp2.convert("L")
bw = gray.point(lambda x: 0 if x < 128 else 255, "1")
bw.save(bitmap_filename)
print("New file saved")

#open the output file in the browser (in a new tab, if possible)
#url = os.path.abspath(output_file.name)
#webbrowser.open('file://' + url, new=2)