import random

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
        resources_score = 0
        #here, we check the number and the type of the adjacent resources
        #we discard nodes with only 2 adjacent resources (desert included), so the ones on the sea
        if len(resources)<3:
            resources_score -=10
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
        return number_score + resources_score



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
        return self.hand

    def on_moving_thief(self):
        terrain = random.randint(0, 18)
        player = -1
        for node in self.board.terrain[terrain]['contacting_nodes']:
            if self.board.nodes[node]['player'] != -1:
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
        elif self.hand.resources.has_this_more_materials(BuildConstants.CITY):
            valid_nodes = self.board.valid_city_nodes(self.id)
            scores = []
            for node in valid_nodes:
                score = super().evaluate_node(self, node, self.board)
                scores.append((node,score))
            scores.sort(key=lambda x: x[1], reverse=True)
            city_node = scores[0][0]
            return {'building': BuildConstants.CITY, 'node_id': valid_nodes[city_node]}
        #after that, 
        # Pueblo / carretera
        if self.hand.resources.has_this_more_materials(BuildConstants.TOWN):
            answer = random.randint(0, 1)
            # Elegimos aleatoriamente si hacer un pueblo o una carretera
            if answer:
                valid_nodes = self.board.valid_town_nodes(self.id)
                scores = []
                for node in valid_nodes:
                     score = super().evaluate_node(self, node, self.board)
                     scores.append((node, score))
                scores.sort(key=lambda x: x[1], reverse=True)
                town_node = scores[0][0]
                return {'building': BuildConstants.TOWN, 'node_id': valid_nodes[town_node]}
            else:
                valid_nodes = self.board.valid_road_nodes(self.id)
                scores = []
                for node in valid_nodes:
                     score = super().evaluate_node(self, node, self.board)
                     scores.append((node, score))
                scores.sort(key=lambda x: x[1], reverse=True)
                road_node = scores[0][0]
                return {'building': BuildConstants.ROAD,
                            'node_id': valid_nodes[road_node]['starting_node'],
                            'road_to': valid_nodes[road_node]['finishing_node']}
        return None

    def on_game_start(self, board_instance):
        self.board = board_instance
        free_nodes = board_instance.valid_starting_nodes()
        
        #evaluation of the available nodes:
        scores = []
        for node in free_nodes:
            score = super().evaluate_node(self, node, self.board)
            scores.append((node, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        node_id = scores[0][0]
        #random allocation for the node
        possible_roads = self.board.nodes[node_id]['adjacent']
        road = possible_roads[random.randint(0, len(possible_roads) - 1)]
        return node_id, road

    def on_monopoly_card_use(self):
        material = random.randint(0, 4)
        return material

    # noinspection DuplicatedCode
    def on_road_building_card_use(self):
        valid_nodes = self.board.valid_road_nodes(self.id)
        if len(valid_nodes) > 1:
            while True:
                road_node = random.randint(0, len(valid_nodes) - 1)
                road_node_2 = random.randint(0, len(valid_nodes) - 1)
                if road_node != road_node_2:
                    return {'node_id': valid_nodes[road_node]['starting_node'],
                            'road_to': valid_nodes[road_node]['finishing_node'],
                            'node_id_2': valid_nodes[road_node_2]['starting_node'],
                            'road_to_2': valid_nodes[road_node_2]['finishing_node'],
                            }
        elif len(valid_nodes) == 1:
            return {'node_id': valid_nodes[0]['starting_node'],
                    'road_to': valid_nodes[0]['finishing_node'],
                    'node_id_2': None,
                    'road_to_2': None,
                    }
        return None

    def on_year_of_plenty_card_use(self):
        material, material2 = random.randint(0, 4), random.randint(0, 4)
        return {'material': material, 'material_2': material2}
