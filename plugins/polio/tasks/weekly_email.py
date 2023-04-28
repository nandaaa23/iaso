from logging import getLogger

from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from beanstalk_worker import task_decorator
from plugins.polio.models import Campaign, CountryUsersGroup, Round
from plugins.polio.serializers import preparedness_from_url

logger = getLogger(__name__)


# TODO Add to message SOPs : Standard operating procedure
#  As per the outbreak response plan the\
#  country has completed (activity done as per SOPs) and is now looking forward to (Next activity on SOPs).


def get_last_preparedness(campaign):
    try:
        round = campaign.rounds.filter(campaign__preparedness__spreadsheet_url__isnull=False).latest("number")
        preparedness_from_url(round.preparedness_spreadsheet_url)
    except Round.DoesNotExist:
        return {}


def send_notification_email(campaign):
    country = campaign.country
    domain = settings.DNS_DOMAIN
    from_email = settings.DEFAULT_FROM_EMAIL

    if not (campaign.obr_name and country and campaign.deleted_at is None):
        print(f"Campaign {campaign} skipped because of missing fields")
        return False
    try:
        cug = CountryUsersGroup.objects.get(country=country)
        lang = cug.language
    except CountryUsersGroup.DoesNotExist:
        return False
    users = cug.users.all()
    emails = [user.email for user in users if user.email]
    if not emails:
        return False
    # day_number = (
    #     (now().date() - campaign.cvdpv2_notified_at).days
    #     if campaign.cvdpv2_notified_at
    #     else "{Error: No cVDPV notification available. Enter a notification date in order to have the days count.}"
    # )
    # onset_days = (
    #     (campaign.cvdpv2_notified_at - campaign.onset_at).days
    #     if campaign.onset_at and campaign.cvdpv2_notified_at
    #     else "{Error: No cVDPV notification or campaign on set available. Enter a date in order to have the days count.}"
    # )
    try:
        first_round = campaign.rounds.earliest("number")
    except Round.DoesNotExist:
        first_round = None

    c = campaign
    url = f"https://{domain}/dashboard/polio/list/campaignId/{campaign.id}"

    # next round
    next_round =  campaign.rounds.filter(started_at__gte=now().date()).order_by("started_at").first()
    next_round_date = next_round.started_at
    next_round_days = (
        (next_round.started_at - campaign.onset_at).days
        if next_round and next_round.started_at and campaign.onset_at
        else ""
    )
    next_round_days_left = (
        ((next_round.started_at) - (now().date())).days
        if next_round and next_round.started_at
        else ""
    )
    # format thousand
    target_population = f"{first_round.target_population:,}" if first_round and first_round.target_population else ""

    preparedness = get_last_preparedness(campaign)

    # French
    if lang == "fr":
        email_text = f"""Cher·ère coordinateur.rice de la GPEI – {country.name},

Statut hebdomadaire: Il reste {next_round_days_left} jours avant le début de la campagne. 
Ci-dessous un résumé des informations de la campagne {c.obr_name} disponibles dans la plateforme. Pour plus de détails, cliquez ici: https://afro-rrt-who.hub.arcgis.com/pages/country-summary. S'il manque des données ou s'il y a des mises à jour à effectuer, cliquez ici {url} pour mettre à jour.

* Date de notification              : {c.cvdpv2_notified_at}
* Date du prochain round (Round {next_round.number})          : {next_round_date if campaign.rounds else None}
* Type de vaccin                    : {c.vaccines}
* Population cible                  : {target_population} 
* RA Date de l'approbation RRT/ORPG  : {c.risk_assessment_rrt_oprtt_approval_at}
* Date de soumission du budget      : {c.submitted_to_rrt_at_WFEDITABLE}
* Lien vers la preperadness google sheet du Round {next_round.number if next_round else None} : {next_round.preparedness_spreadsheet_url if next_round else None}
* Prep. national                 : {preparedness.get('national_score') if preparedness else ''}
* Prep. régional                 : {preparedness.get('regional_score') if preparedness else ''}
* Prep. district                 : {preparedness.get('district_score') if preparedness else ''}

Pour toute question, contacter l'équipe RRT.
Ceci est un message automatique.
    """
    # Portuguese
    elif lang == "pt":
        email_text = f"""Prezado(a) coordenador(a) da GPEI – {country.name},

Estado semanal: passaram-se {next_round_days} dias desde a data de notificação da campanha.
Segue em baixo um resumo das informações da campanha {c.obr_name} disponíveis na plataforma. Para mais detalhes, clique em: https://afro-rrt-who.hub.arcgis.com/pages/country-summary . Se faltarem dados ou houverem atualizações a serem feitas, por favor clique em {url} para atualizar.

* Data de notificação: {c.cvdpv2_notified_at}
* Proxima ronda (Round {next_round.number}) data: {next_round_date if campaign.rounds else None}
* Tipo de vacina: {c.vaccines}
* População-alvo: {target_population}
* RA Data de aprovação RRT/ORPG: {c.risk_assessment_rrt_oprtt_approval_at}
* Data de envio do orçamento:   {c.submitted_to_rrt_at_WFEDITABLE}
* Link to {next_round.number if next_round else None}  preparedness Google sheet: {next_round.preparedness_spreadsheet_url if next_round else None}
* Prep. nacional: {preparedness.get('national_score') if preparedness else ''}
* Prep. regional: {preparedness.get('regional_score') if preparedness else ''}
* Prep. distrital: {preparedness.get('district_score') if preparedness else ''}

Por favor, em caso de qualquer dúvida entre em contato com a equipa RRT.
Esta é uma mensagem automática.
    """
    # English
    else:
        email_text = f"""Dear GPEI coordinator – {country.name},

Weekly status update: Today is day {next_round_days} to Round {next_round.number} start date.
Below is the summary of the campaign {c.obr_name}. For more details, visit https://afro-rrt-who.hub.arcgis.com/pages/country-summary
If there are missing data or dates; visit {url} to update

* Notification date              : {c.cvdpv2_notified_at}
* Next round (Round {next_round.number}) date: {next_round_date if campaign.rounds else None}
* Vaccine Type                   : {c.vaccines}
* Target population              : {target_population} 
* RA RRT/ORPG approval date      : {c.get_risk_assessment_status_display() or 'Pending'}
* Date Budget Submitted          : {c.submitted_to_rrt_at_WFEDITABLE}
* Link to Round {next_round.number if next_round else None} preparedness Google sheet: {next_round.preparedness_spreadsheet_url if next_round else None}
* Prep. national                 : {preparedness.get('national_score') if preparedness else ''}
* Prep. regional                 : {preparedness.get('regional_score') if preparedness else ''}
* Prep. district                 : {preparedness.get('district_score') if preparedness else ''}

For guidance on updating: contact RRT team
Timeline tracker Automated message.
    """

    logger.info(f"Sending to {len(emails)} recipients")

    send_mail(
        "Update on Campaign {}".format(campaign.obr_name),
        email_text,
        from_email,
        emails,
    )

    return True


@task_decorator(task_name="send_weekly_email")
def send_email(task=None):
    campaigns = Campaign.objects.exclude(enable_send_weekly_email=False)
    total = campaigns.count()
    email_sent = 0

    for i, campaign in enumerate(campaigns):

        task.report_progress_and_stop_if_killed(
            progress_value=i,
            end_value=total,
            progress_message=f"Campaign {campaign.pk} started",
        )

        latest_round_end = campaign.rounds.order_by("ended_at").last()
        if latest_round_end and latest_round_end.ended_at and latest_round_end.ended_at <  now().date():
            print(f"Campaign {campaign} is finished, skipping")
            continue
        logger.info(f"Email for {campaign.obr_name}")
        status = send_notification_email(campaign)
        if not status:
            logger.info(f"... skipped")
        else:
            email_sent += 1

    task.report_success(f"Finished sending {email_sent} weekly-email(s)")
