odoo.define("dsl_fleet_management.Dashboard", function (require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var web_client = require('web.web_client');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var _t = core._t;
    var rpc = require('web.rpc');
    var self = this;
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var DashBoard = AbstractAction.extend({
        contentTemplate: 'main_template_dashboard',
        init: function(parent, context) {
            this._super(parent, context);
            this.dashboard_templates = ['main_template_dashboard'];
        },
        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                 self.fetch_data();
                self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
                self.bind_click_event();;
            });
        },
 
        render_graphs: function () {
         var self = this;
         self.render_team_ticket_count_services_graph();
         self.render_team_ticket_count_refueling_request_graph();
         
         
     },
 
        willStart: function(){
            var self = this;
            return this._super()
        },
       
        render_dashboards: function() {
            var self = this;
            this.fetch_data()
            var templates = []
            var templates = ['main_template_dashboard'];
            _.each(templates, function(template) {
                self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}))
                
            });
           
            
        },
        

        render_team_ticket_count_services_graph: function () {
            var self = this;
            var ctx = self.$(".team_ticket_count");
        
            rpc.query({
                model: "dsl.fleet.dashboard",
                method: "get_team_ticket_count_services_pie",
            }).then(function (data) {
                var datasets = [{
                    data: [],
                    backgroundColor: [],
                    borderColor: [],
                    borderWidth: 1
                }];
        
                data.forEach(function (record) {
                    datasets[0].data.push(record.value);
                    datasets[0].backgroundColor.push(record.color);
                    datasets[0].borderColor.push(record.color);
                });
        
                var chartData = {
                    datasets: datasets,
                    labels: data.map(function (record) {
                        return record.label;
                    })
                };
        
                var options = {
                    responsive: true,
                    title: false,
                    maintainAspectRatio: true,
                    legend: {
                        display: false
                    },
                    scales: {
                        yAxes: [{
                            display: true,
                            ticks: {
                                beginAtZero: true,
                                steps: 10,
                                stepValue: 5,
                            }
                        }]
                    }
                };
        
                var chart = new Chart(ctx, {
                    type: "pie",
                    data: chartData,
                    options: options
                });
            });
        },

        render_team_ticket_count_refueling_request_graph: function () {
            var self = this;
            var ctx = self.$(".vehicle_refueling_count");
        
            rpc.query({
                model: "dsl.fleet.dashboard",
                method: "get_team_ticket_count_refueling_pie",
            }).then(function (data) {
                var datasets = [{
                    data: [],
                    backgroundColor: [],
                    borderColor: [],
                    borderWidth: 1
                }];
        
                data.forEach(function (record) {
                    datasets[0].data.push(record.value);
                    datasets[0].backgroundColor.push(record.color);
                    datasets[0].borderColor.push(record.color);
                });
        
                var chartData = {
                    datasets: datasets,
                    labels: data.map(function (record) {
                        return record.label;
                    })
                };
        
                var options = {
                    responsive: true,
                    title: false,
                    maintainAspectRatio: true,
                    legend: {
                        display: false
                    },
                    scales: {
                        yAxes: [{
                            display: true,
                            ticks: {
                                beginAtZero: true,
                                steps: 10,
                                stepValue: 5,
                            }
                        }]
                    }
                };
        
                var chart = new Chart(ctx, {
                    type: "bar",
                    data: chartData,
                    options: options
                });
            });
        },

     
        fetch_data: function() {
            var self = this
 //          fetch data to the tiles
            var def1 = this._rpc({
                model: 'dsl.fleet.dashboard',
                method: "get_model_data",
            })
            .then(function (result) {
                $('#total_vehicle').append('<span>' + result.total_vehicle + '</span>');
                $('#total_driver').append('<span>' + result.total_driver + '</span>');
                $('#total_model').append('<span>' + result.total_model + '</span>');
                $('#total_refueling').append('<span>' + result.total_refueling + '</span>');
                $('#total_services').append('<span>' + result.total_services + '</span>');
                $('#accidental_case').append('<span>' + result.accidental_case + '</span>');
            });
        },
        bind_click_event: function () {
            this.$('.vehicles').click(this.vehicles.bind(this));
            this.$('.drivers').click(this.drivers.bind(this));
            this.$('.refuels').click(this.refuels.bind(this));
            this.$('.services').click(this.services.bind(this));
            this.$('.accidentals').click(this.accidentals.bind(this));
            this.$('.models').click(this.models.bind(this));
        },

        vehicles: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            this.do_action({
                name: "Vehicles",
                type: 'ir.actions.act_window',
                res_model: 'fleet.vehicle',
                view_mode: 'list,kanban,form',
                views: [
                    [false, 'list'],
                    [false, 'kanban'],
                    [false, 'form']
                ],
                target: 'current'
            });
        },

        drivers: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            this.do_action({
                name: "Vehicles",
                type: 'ir.actions.act_window',
                res_model: 'fleet.vehicle',
                view_mode: 'list,kanban,form',
                views: [
                    [false, 'list'],
                    [false, 'kanban'],
                    [false, 'form']
                ],
                target: 'current'
            });
        },

        refuels: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            this.do_action({
                name: "Refueling",
                type: 'ir.actions.act_window',
                res_model: 'dsl.vehicle.refueling',
                view_mode: 'list,form',
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                target: 'current'
            });
        },

        services: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            this.do_action({
                name: "Services",
                type: 'ir.actions.act_window',
                res_model: 'fleet.vehicle.log.services',
                view_mode: 'list,form',
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                target: 'current'
            });
        },

        accidentals: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            this.do_action({
                name: "Accidental Case",
                type: 'ir.actions.act_window',
                res_model: 'dsl.accidental.case',
                view_mode: 'list,form',
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                target: 'current'
            });
        },

        models: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();

            this.do_action({
                name: "Models",
                type: 'ir.actions.act_window',
                res_model: 'fleet.vehicle.model',
                view_mode: 'list,form',
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                target: 'current'
            });
        },
 
        
    });


    core.action_registry.add('dsl_fleet_management', DashBoard);
    return DashBoard;
 });