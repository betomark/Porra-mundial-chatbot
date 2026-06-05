import urls
import utils.sofascore_client

def clean_pre_event(evento):
    evento_limpio = {
        "id": evento["id"],
        "customId": evento["customId"],
        "slug": evento["slug"],
        "startTimestamp": evento["startTimestamp"],
        "homeTeam": {
            "id": evento["homeTeam"]["id"],
            "name": evento["homeTeam"]["name"],
            "ranking": evento["homeTeam"]["ranking"],
            "namecode": evento["homeTeam"]["nameCode"]
        },
        "awayTeam": {
            "id": evento["awayTeam"]["id"],
            "name": evento["awayTeam"]["name"],
            "ranking": evento["awayTeam"]["ranking"],
            "namecode": evento["awayTeam"]["nameCode"]
        },
        "tournament": {
            "id": evento["uniqueTournament"]["id"],
            "name": evento["uniqueTournament"]["name"]
        },
        "season": {
            "id": evento["season"]["id"],
            "name": evento["season"]["name"]
        }
    }

    return evento_limpio

def clean_past_event(evento):
    evento_limpio = clean_pre_event(evento)
    evento_limpio["homeScore"] = evento["homeScore"]
    evento_limpio["awayScore"] = evento["awayScore"]
    #TODO: añadir más campos relevantes de eventos pasados, como goleadores, tarjetas, etc.
    return evento_limpio


def get_odds(event_id):
    url = urls.MATCH_ODDS.format(event_id=event_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    print(f"Obteniendo cuotas para el evento {event_id} desde {url}...")
    
    return sofascore_client.get(url)
