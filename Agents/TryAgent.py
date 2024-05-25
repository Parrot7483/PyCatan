import random
import math

from Classes.Constants import MaterialConstants, BuildConstants
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Interfaces.AgentInterface import AgentInterface


class TryAgent(AgentInterface):
    """
    Es necesario poner super().nombre_de_funcion() para asegurarse de que coge la función del padre
    """
    def __init__(self, agent_id):
        super().__init__(agent_id)


    def evaluate_node(self, node_id, board_instance):
        self.board = board_instance
        numbers = [self.board.terrain[v]['probability'] for v in self.board.nodes[node_id]['contacting_terrain']]
        # print(f"probability of neightbors from node_id {node_id}: {numbers}")
        number_score = 0

        #here, for each adjacent terrain, we assign a score based on the probability of the associated number
        for number in numbers:
            if number in [6, 8]:
                number_score += 3
            elif number in [5, 9]:
                number_score += 2
            elif number in [4, 10]:
                number_score += 1
            elif number in [3, 11]:
                number_score -= 1
            elif number in [2, 12]:
                number_score -= 2

        resources = [self.board.terrain[v]['terrain_type'] for v in self.board.nodes[node_id]['contacting_terrain']]
        # print(f"terrain_type of neightbors from node_id {node_id}: {resources}")

        #here, we check the number and the type of the adjacent resources
        #we discard nodes with only 2 adjacent resources (desert included), so the ones on the sea
        resource_score = 0
        if len(resources)<3:
            resource_score -= 10
        for resource in resources: #to do enum
            if resource == 1: #mineral
                resource_score += 3
            elif resource == 0: #cereal
                resource_score += 2
            elif resource in [3, 2]: #wood or clay
                resource_score += 1
            elif resource == 4: #wool
                resource_score -= 1
            elif resource == -1: #desert
                resource_score -= 5 #we discard nodes with the desert adjacent

        return number_score + resource_score
    
    def best_node(self, nodes, board_instance):
        best_node = None
        best_score = -math.inf 

        for node in nodes: 
            score = self.evaluate_node(node, board_instance)
            if score > best_score:
                best_score = score
                best_node = node
                
        return best_node


    def evaluate_terrain(self, terrain_id, board_instance):
        #similar to node scoring,
        #assign a score to a terrain based on the resource and the number
        #avoiding terrains in which I have a town or city
        self.board = board_instance
        number = self.board.terrain[terrain_id]['probability']
        number_score = 0
        if number in [6, 8]:
            number_score += 3
        elif number in [5, 9]:
            number_score += 2
        elif number in [4, 10]:
            number_score += 1
        elif number in [3, 11]:
            number_score -= 1
        elif number in [2, 12]:
            number_score -= 2
        
        resource = self.board.terrain[terrain_id]['terrain_type']
        resource_score = 0
        if resource == 1: #mineral
            resource_score += 3
        elif resource == 0: #cereal
            resource_score += 2
        elif resource in [3, 2]: #wood or clay
            resource_score += 1
        elif resource == 4: #wool
            resource_score -= 1
        elif resource == -1: #desert
            resource_score -= 5
        
        im_here = False
        for node in self.board.terrain[terrain_id]['contacting_nodes']:
            if self.board.nodes[node]['player'] == self.id:
                im_here = True
        if im_here:
            return -100
        else:
            return number_score + resource_score
        
    
    def best_terrain(self, terrains, board_instance):
        best_terrain = None
        best_score = -math.inf 

        for terrain in terrains: 
            score = self.evaluate_terrain(terrain, board_instance)
            if score > best_score:
                best_score = score
                best_terrain = terrain
                
        return best_terrain





    def on_trade_offer(self, board_instance, incoming_trade_offer=TradeOffer(), player_making_offer=int):
        gives = incoming_trade_offer.gives
        receives = incoming_trade_offer.receives
        #accept if they offer mineral without asking for it, asking for at most 3 other cards
        if gives.mineral>0 and sum(receives.array_ids)<4 and receives.mineral==0:
            return True
        #refuse if they offer only wool
        elif gives.wool == sum(gives.array_ids) and gives.wool>0:
            return False
        #if they offer more than they ask, but not mineral, accept
        elif sum(receives.array_ids) <= sum(gives.array_ids) and receives.mineral==0:
            return True
        #accept preferred couples 
        elif self.hand.resources.mineral>0 and gives.cereal>0:
            return True
        elif self.hand.resources.wood>0 and gives.clay>0:
            return True
        elif self.hand.resources.clay>0 and gives.wood>0:
            return True
        else:
            return False

    def on_turn_start(self):
        # self.development_cards_hand.add_card(DevelopmentCard(99, 0, 0))
        if len(self.development_cards_hand.check_hand()) and random.randint(0, 1):
            return self.development_cards_hand.select_card_by_id(self.development_cards_hand.hand[0].id)
        return None

    def on_having_more_than_7_materials_when_thief_is_called(self):
        while self.hand.get_total() > 7:
            while self.hand.resources.wool > 1: #firstly wool, keeping only one of it
                    self.hand.remove_material(4, 1)
            for node in range(54):
                if self.board.nodes[node]['player'] == self.id:
                    for terrain in self.board.nodes[node]['contacting_terrain']:
                        if self.board.terrains[terrain]['terrain_type'] != -1:
                            self.hand.remove_material(self.board.terrains[terrain]['terrain_type'],1)
        return self.hand

    def on_moving_thief(self):
        terrains = range(19)
        terrain = self.best_terrain(terrains, self.board)
        player = -1
       #choose the player near to that terrain 
        for node in self.board.terrain[terrain]['contacting_nodes']:
            if self.board.nodes[node]['player'] != -1 and self.board.nodes[node]['player'] != self.id:
                player = self.board.nodes[node]['player']
        return {'terrain': terrain, 'player': player}

    def on_turn_end(self):
        if len(self.development_cards_hand.check_hand()) and random.randint(0, 1):
            return self.development_cards_hand.select_card_by_id(self.development_cards_hand.hand[0].id)
        return None

    def on_commerce_phase(self):
        if len(self.development_cards_hand.check_hand()) and random.randint(0, 1):
            return self.development_cards_hand.select_card_by_id(self.development_cards_hand.hand[0].id)

        answer = random.randint(0, 1)
        if answer:
            if self.hand.resources.cereal >= 4:
                return {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.MINERAL}
            if self.hand.resources.mineral >= 4:
                return {'gives': MaterialConstants.MINERAL, 'receives': MaterialConstants.CEREAL}
            if self.hand.resources.clay >= 4:
                return {'gives': MaterialConstants.CLAY, 'receives': MaterialConstants.CEREAL}
            if self.hand.resources.wood >= 4:
                return {'gives': MaterialConstants.WOOD, 'receives': MaterialConstants.CEREAL}
            if self.hand.resources.wool >= 4:
                return {'gives': MaterialConstants.WOOL, 'receives': MaterialConstants.CEREAL}

            return None
        else:
            gives = Materials(random.randint(0, self.hand.resources.cereal),
                              random.randint(0, self.hand.resources.mineral),
                              random.randint(0, self.hand.resources.clay),
                              random.randint(0, self.hand.resources.wood),
                              random.randint(0, self.hand.resources.wool))
            receives = Materials(random.randint(0, self.hand.resources.cereal),
                                 random.randint(0, self.hand.resources.mineral),
                                 random.randint(0, self.hand.resources.clay),
                                 random.randint(0, self.hand.resources.wood),
                                 random.randint(0, self.hand.resources.wool))
            trade_offer = TradeOffer(gives, receives)
            return trade_offer

    def on_build_phase(self, board_instance):
        self.board = board_instance

        #we keep random choice of playing a development card or not
        if len(self.development_cards_hand.check_hand()) and random.randint(0, 1):
            return self.development_cards_hand.select_card_by_id(self.development_cards_hand.hand[0].id)
        #then, priority to development cards
        elif self.hand.resources.has_this_more_materials(BuildConstants.CARD):
            return {'building': BuildConstants.CARD}

        #choice of the node for building city/town/road: node evaluation as for game_start

        #after that, cities:
        elif self.hand.resources.has_this_more_materials(BuildConstants.CITY) and len(self.board.valid_city_nodes(self.id)) > 0:
            valid_nodes = self.board.valid_city_nodes(self.id)
            city_node = self.best_node(valid_nodes, self.board)

            return {'building': BuildConstants.CITY, 'node_id': city_node}

        #after that, 
        # Pueblo / carretera
        if self.hand.resources.has_this_more_materials(BuildConstants.TOWN):
            answer = random.randint(0, 1)
            # Elegimos aleatoriamente si hacer un pueblo o una carretera
            if answer and len(self.board.valid_town_nodes(self.id)) > 0:
                valid_nodes = self.board.valid_town_nodes(self.id)
                town_node = self.best_node(valid_nodes, self.board)
                return {'building': BuildConstants.TOWN, 'node_id': town_node}

            elif len(self.board.valid_road_nodes(self.id)) > 0:
                valid_nodes = self.board.valid_road_nodes(self.id)
                
                best_start = None
                best_finish = None
                best_score = -math.inf

                for v in valid_nodes: 
                    start, finish = v["starting_node"], v["finishing_node"]
                    score = self.evaluate_node(finish, self.board)
                    
                    if score > best_score:
                        best_start = start
                        best_finish = finish
                        best_score = best_score

                return {'building': BuildConstants.ROAD,
                            'node_id': best_start,
                            'road_to': best_finish}

        return None

    def on_game_start(self, board_instance):
        self.board = board_instance
        free_nodes = board_instance.valid_starting_nodes()
        
        #evaluation of the available nodes:
        node_id = self.best_node(free_nodes, board_instance)
        #random allocation for the road
        possible_roads = self.board.nodes[node_id]['adjacent']
        road = possible_roads[random.randint(0, len(possible_roads) - 1)]
        return node_id, road

    def on_monopoly_card_use(self):
        return 1

    # noinspection DuplicatedCode
    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            scores = []
            for v in valid_nodes: 
                start, finish = v["starting_node"], v["finishing_node"]
                score = self.evaluate_node(finish, self.board)
                scores.append((start,finish, score))
            scores.sort(key=lambda x: x[1], reverse = True)
            return{'node_id':scores[0][0],
                   'road_to':scores[0][1],
                   'node_id_2': scores[1][0],
                   'road_to_2': scores[1][1]}
        elif len(valid_nodes) == 1:
            return {'node_id': valid_nodes[0]['starting_node'],
                    'road_to': valid_nodes[0]['finishing_node'],
                    'node_id_2': None,
                    'road_to_2': None,
                    }
        return None

    def on_year_of_plenty_card_use(self):
        return {'material': 1, 'material_2': 0}
