$(document).ready(function () {
    // Contact Form Handler
    var contactForm = $(".contact-form")
    var contactFormMethod = contactForm.attr("method")
    var contactFormEndpoint = contactForm.attr("action")


    // search button spinner
    function displayContactSubmiting(submitBtn, defaultTxt, doSubmit) {
        if (doSubmit) {
            submitBtn.addClass("disabled")
            submitBtn.html("<i class='fa fa-spinner'></i> Sending...")
        } else {
            submitBtn.removeClass("disabled")
            submitBtn.html(defaultTxt)
        }

    }

    contactForm.submit(function (event) {
        event.preventDefault()
        var thisForm = $(this)
        var contactFormData = contactForm.serialize()
        var contactBtn = contactForm.find("[type='submit']")
        var contactBtnTxt = contactBtn.text()
        displayContactSubmiting(contactBtn, contactBtnTxt, true)
        // ajax call
        $.ajax({
            method: contactFormMethod,
            url: contactFormEndpoint,
            data: contactFormData,
            success: function (data) {
                thisForm[0].reset()
                $.alert({
                    title: "Success!",
                    content: data.message,
                    theme: "modern",
                })
                setTimeout(function () {
                    displayContactSubmiting(contactBtn, contactBtnTxt, false)
                }, 500)
            },
            // ajax error handling of the contact form
            error: function (errorData) {
                console.log(errorData.responseJSON)
                var jsonData = errorData.responseJSON
                var msg = ""

                $.each(jsonData, function (key, value) {
                    msg += key + "" + value[0].message + "<br/>"
                })

                $.alert({
                    title: "Oops!",
                    content: msg,
                    theme: "modern",
                })
                setTimeout(function () {
                    displayContactSubmiting(contactBtn, contactBtnTxt, false)
                }, 500)
            }
        })

    })



    // auto search function
    var searchForm = $(".search-form")
    var searchInput = searchForm.find("[name='q']") // find the input field in the search area using a class
    var typingTimer; // when will the first time this function triggert
    var typingInterval = 500 // 0.5 seconds (milli seconds) between check of input
    var searchBtn = searchForm.find("[type='submit']")
    // key released
    searchInput.keyup(function (event) {
        clearTimeout(typingTimer)
        typingTimer = setTimeout(performSearch, typingInterval)

    })
    // key pressed
    searchInput.keydown(function (event) {
        clearTimeout(typingTimer)

    })
    // search button spinner
    function displaySearching() {
        searchBtn.addClass("disabled")
        searchBtn.html("<i class='fa fa-spinner'></i> searching...")
    }
    // perform the search function
    function performSearch() {
        displaySearching()
        var query = searchInput.val()
        // timeout to show the search does something
        setTimeout(function () {
            window.location.href = "/search/?q=" + query
        }, 750)

    }


    // cart add and remove logic AJAX
    var productForm = $(".form-product-ajax")
    productForm.submit(function (event) {
        event.preventDefault();
        var thisForm = $(this);
        //var actionEndpoint = thisForm.attr("action");
        var actionEndpoint = thisForm.attr("data-endpoint");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();


        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function (data) {
                var submitSpan = thisForm.find(".submit-span")
                if (data.added) {
                    submitSpan.html('<button type="submit" class="btn btn-danger">Remove from Cart</button>')
                } else {
                    submitSpan.html('<button type="submit" class="btn btn-success">add to cart</button>')
                }
                var navbarCount = $(".navbar-cart-count")
                navbarCount.text(data.cartItemCount)
                var currentPath = window.location.href
                if (currentPath.indexOf("cart") != -1) {
                    refreshCart()
                }

            },
            error: function (errorData) {
                $.alert({
                    title: "Oops!",
                    content: "An error occured",
                    theme: "modern",
                })

            }

        })
    })
    function refreshCart() {
        var cartTable = $(".cart-table");
        var cartBody = cartTable.find(".cart-body");
        var productsRows = cartBody.find(".cart-products")
        var currentUrl = window.location.href

        var refreshCartUrl = "/api/cart/";
        var refreshCartMethod = "GET";
        var data = {};
        console.log("before Ajax call")
        $.ajax({
            url: refreshCartUrl,
            method: refreshCartMethod,
            data: data,
            success: function (data) {
                console.log("success refresh")
                console.log(data)
                var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
                if (data.products.length > 0) {
                    productsRows.html(" ")
                    i = data.products.length
                    $.each(data.products, function (index, value) {
                        var newCartItemRemove = hiddenCartItemRemoveForm.clone()
                        newCartItemRemove.css("display", "block")
                        newCartItemRemove.find(".cart-item-product-id").val(data.id)
                        cartBody.prepend("<tr><th scope='row'>" + i + "</th><td><a href='" + value.url + "'>" + value.name + "</a></td><td>" + value.price + "</td><td>" + newCartItemRemove.html() + "</td></tr>")
                        i--
                    })

                    cartBody.find(".cart-subtotal").text(data.subtotal)
                    cartBody.find(".cart-total").text(data.total)

                } else {
                    window.location.href = currentUrl
                    console.log("not working")
                }

            },
            error: function (errorData) {
                $.alert({
                    title: "Oops!",
                    content: "An error occured",
                    theme: "modern",
                })
            }

        })

    }
})