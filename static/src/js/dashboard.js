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

        
     
    //     render_team_ticket_count_graph: function () {
    //      var self = this
    //      var ctx = self.$(".vehicle_refueling_count");
    //      rpc.query({
    //          model: "dsl.fleet.dashboard",
    //          method: "get_team_ticket_count_pie",
    //      }).then(function (arrays) {
    //          var data = {
    //              labels: arrays[1],
    //              datasets: [{
    //                  label: "",
    //                  data: arrays[0],
    //                  backgroundColor: [
    //                      'rgba(255, 99, 132, 0.2)',
    //                      'rgba(255, 159, 64, 0.2)',
    //                      'rgba(255, 205, 86, 0.2)',
    //                      'rgba(75, 192, 192, 0.2)',
    //                      'rgba(54, 162, 235, 0.2)',
    //                      'rgba(153, 102, 255, 0.2)',
    //                      'rgba(201, 203, 207, 0.2)'
    //                  ],
    //                  borderColor: ['rgb(255, 99, 132)',
    //                      'rgb(255, 159, 64)',
    //                      'rgb(255, 205, 86)',
    //                      'rgb(75, 192, 192)',
    //                      'rgb(54, 162, 235)',
    //                      'rgb(153, 102, 255)',
    //                      'rgb(201, 203, 207)'
    //                  ],
    //                  borderWidth: 1
    //              },]
    //          };
 
    //          //options
    //          var options = {
    //              responsive: true,
    //              title: false,
    //              maintainAspectRatio: true,
    //              legend: {
    //                  display: false //This will do the task
    //              },
    //              scales: {
    //                  yAxes: [{
    //                      display: true,
    //                      ticks: {
    //                          beginAtZero: true,
    //                          steps: 10,
    //                          stepValue: 5,
    //                          // max: 100
    //                      }
    //                  }]
    //              }
    //          };
 
    //          // create Chart class object
    //          var chart = new Chart(ctx, {
    //              type: "bar",
    //              data: data,
    //              options: options
    //          });
    //      });
    //  },
 
     
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
 
        
    });


    core.action_registry.add('dsl_fleet_management', DashBoard);
    return DashBoard;
 });