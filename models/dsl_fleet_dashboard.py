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
        total_refueling = self.env['dsl.vehicle.refueling'].search([])
        accidental_case = self.env['dsl.accidental.case'].search([])
        total_services = self.env['fleet.vehicle.log.services'].search([])
        return {
            'total_vehicle': len(total_vehicle),
            'total_driver': len(total_driver),
            'total_model':len(total_model),
            'total_refueling':len(total_refueling),
            'total_services':len(total_services),
            'accidental_case':len(accidental_case),
           
        }
    



    @api.model
    def get_team_ticket_count_services_pie(self):
        tickets = self.env['fleet.vehicle.log.services'].search([])
        team_counts = {}

        for ticket in tickets:
            team = ticket.user_id.name
            if team not in team_counts:
                team_counts[team] = 1
            else:
                team_counts[team] += 1

        data = []
        colors = [
            'rgba(255, 99, 132, 0.4)',
            'rgba(255, 159, 64, 0.5)',
            'rgba(255, 205, 86, 0.3)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(54, 162, 235, 0.9)',
            'rgba(153, 102, 255, 0.4)',
            'rgba(201, 203, 207, 0.6)'
        ]
        color_index = 0

        for team, count in team_counts.items():
            data.append({
                'label': team,
                'value': count,
                'color': colors[color_index]
            })
            color_index = (color_index + 1) % len(colors)

        return data
    

    
    @api.model
    def get_team_ticket_count_refueling_pie(self):
        tickets = self.env['dsl.vehicle.refueling'].search([])
        team_counts = {}

        for ticket in tickets:
            team = ticket.user_id.name
            if team not in team_counts:
                team_counts[team] = 1
            else:
                team_counts[team] += 1

        data = []
        colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(255, 159, 64, 0.5)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(201, 203, 207, 0.6)'
        ]
        color_index = 0

        for team, count in team_counts.items():
            data.append({
                'label': team,
                'value': count,
                'color': colors[color_index]
            })
            color_index = (color_index + 1) % len(colors)

        return data 


