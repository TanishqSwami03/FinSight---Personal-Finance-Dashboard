/*! For license information please see investment-company-shares.js.LICENSE.txt */
"use strict";function lastvisibletd(){}document.addEventListener("DOMContentLoaded",(function(){window.randomScalingFactor=function(){return Math.round(20*Math.random())};var a=document.getElementById("summarychart").getContext("2d"),t=a.createLinearGradient(0,0,0,280);t.addColorStop(0,"rgba(0, 73, 232, 0.8)"),t.addColorStop(.5,"rgba(229, 10, 142, 0.5)"),t.addColorStop(1,"rgba(252, 122, 30, 0)");var n={type:"line",data:{labels:["10:30","11:00","11:30","12:00","12:30","01:00","01:30"],datasets:[{label:"# of Votes",data:[randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor(),randomScalingFactor()],radius:0,backgroundColor:t,borderColor:"#5840ef",borderWidth:1,fill:!0,tension:.5}]},options:{animation:!0,maintainAspectRatio:!1,plugins:{legend:{display:!1}},scales:{y:{display:!0,beginAtZero:!0},x:{grid:{display:!0},display:!0,beginAtZero:!0}}}},o=new Chart(a,n);setInterval((function(){n.data.datasets.forEach((function(a){a.data=a.data.map((function(){return randomScalingFactor()}))})),o.update()}),3e3)})),window.addEventListener("resize",(function(a){}));