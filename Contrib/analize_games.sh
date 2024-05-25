#!/usr/bin/env bash

set -e

# Check if the number of arguments is exactly 1
if [ $# -ne 1 ]; then
    echo "Usage: $0 <file>"
    echo "where <file> is the games.json of a simulation"
    exit 1
fi

# Check if the argument is a file
if [ ! -f "$1" ]; then
    echo "Error: '$1' is either missing or not a file."
    exit 1
fi

get_winner() {
    local json_object="$1"

    # Get the last round of the game
    local max_round=$(echo "$json_object" | jq -r '.game | keys[]' | sed 's/round_//' | sort -n | tail -n 1 | sed 's/^/round_/')

    # Initialize a variable to store the last non-null value
    local last_non_null=""

    # Check each jq command, and update the variable if the result is not null
    if [ "$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P0.end_turn.victory_points')" != "null" ]; then
        last_non_null=$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P0.end_turn.victory_points')
    fi

    if [ "$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P1.end_turn.victory_points')" != "null" ]; then
        last_non_null=$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P1.end_turn.victory_points')
    fi

    if [ "$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P2.end_turn.victory_points')" != "null" ]; then
        last_non_null=$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P2.end_turn.victory_points')
    fi

    if [ "$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P3.end_turn.victory_points')" != "null" ]; then
        last_non_null=$(echo "$json_object" | jq --arg max_round "$max_round" '.game[$max_round].turn_P3.end_turn.victory_points')
    fi

    # Extract the winner
    local result=$(echo "$last_non_null" | jq -r 'to_entries | max_by(.value) | .key')

    echo "$result"
}

games="$(jq 'length' $1)"
echo "Number of games: $games"

wins_j0="0"
wins_j1="0"
wins_j2="0"
wins_j3="0"

echo -n "Winner: "
# Iterate over each object in the array
while read -r obj; do
    winner=$(get_winner "$obj")

    # Iterate over each player and explicitly increment their count
    if [[ "$winner" == "J0" ]]; then
        wins_j0=$(( wins_j0 + 1 ))
        echo -n "J0 "
    elif [[ "$winner" == "J1" ]]; then
        wins_j1=$(( wins_j1 + 1 ))
        echo -n "J1 "
    elif [[ "$winner" == "J2" ]]; then
        wins_j2=$(( wins_j2 + 1 ))
        echo -n "J2 "
    elif [[ "$winner" == "J3" ]]; then
        wins_j3=$(( wins_j3 + 1 ))
        echo -n "J3 "
    fi
done < <(jq -c '.[]' "$1")

echo ""
echo "Result: "
echo "J0: $wins_j0 ($(( $wins_j0 * 100 / games ))%)"
echo "J1: $wins_j1 ($(( $wins_j1 * 100 / games ))%)"
echo "J2: $wins_j2 ($(( $wins_j2 * 100 / games ))%)"
echo "J3: $wins_j3 ($(( $wins_j3 * 100 / games ))%)"


