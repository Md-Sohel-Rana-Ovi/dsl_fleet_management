from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class FleetDashboard(models.Model): 
    _name = 'dsl.fleet.dashboard'

    @api.model
    def get_model_data(self):
        """Returns data to the tiles of dashboard"""
        total_vehicle = self.env['fleet.vehicle'].search([])
        total_driver = self.env['fleet.vehicle'].search([])
        total_model = self.env['fleet.vehicle.model'].search([])
        total_refueling = self.env['dsl.vehicle.refueling'].search([('state', '=', 'bill')])
        _logger.info(len(total_refueling))
        _logger.info(len(total_refueling))
        _logger.info(len(total_refueling))
        total_services = self.env['fleet.vehicle.log.services'].search([('state', '=', 'bill')])
        return {
            'total_vehicle': len(total_vehicle),
            'total_driver': len(total_driver),
            'total_model':len(total_model),
            'total_refueling':len(total_refueling),
            'total_services':len(total_services),
           
        }

    
    @api.model
    def get_team_ticket_count_pie(self):
        """bar chart"""
        ticket_count = []
        team_list = []
        tickets = self.env['fleet.vehicle'].search([])

        for rec in tickets:
            if rec:
                team = rec.name
                if team not in team_list:
                    team_list.append(team)
                    ticket_count.append(team)
                # ticket_count.append(team)

        value = len(ticket_count)
        team_val = []
        team_val.append({'label': "total_vehicle", 'value': value})
        # for index in range(len(team_list)):
        #     # value = ticket_count.count(team_list[index])
        #     value = len(ticket_count)
        #     team_name = team_list[index]
        #     team_val.append({'label': "total_vehicle", 'value': value})
        name = []
        for record in team_val:
            name.append(record.get('label'))
        #
        count = []
        for record in team_val:
            count.append(record.get('value'))
        #
        team = [count, name]
        return team
    
   


