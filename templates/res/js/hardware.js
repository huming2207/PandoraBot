'use strict';

var vueData =
    {
        status: "Unknown",
        result: "Unknown",
        currentValue: "Unknown",
        pin: "",
        newValue: ""
    };

window.onload = function (ev) {
    var vueInstance = new Vue(
    {
        el: '#gpio',
        data: vueData,
        methods: {
            gpioSet: function () {
                axios.get("/gpio_out", {
                    params: {
                        pin: vueData.pin,
                        value: vueData.newValue
                    }
                })
                    .then(function (response) {
                        vueData.result = response.data.status;
                        alert(response.data.message);
                    })
                    .catch(function (error) {
                        console.log("Oops, request failed!");
                        console.log(error.response.data);
                        console.log(error.response.status);
                        console.log(error.response.headers);
                    });
            },

            gpioGet: function () {
                axios.get("/gpio_in", {
                    params: {
                        pin: vueData.pin
                    }
                })
                    .then(function (response) {
                        vueData.result = response.data.message
                    })
                    .catch(function (error) {
                        console.log("Oops, request failed!");
                        console.log(error.response.data);
                        console.log(error.response.status);
                        console.log(error.response.headers);
                    });
            }
        }
    });
};

