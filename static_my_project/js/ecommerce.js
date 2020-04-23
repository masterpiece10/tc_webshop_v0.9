$(document).ready(function () {
    //-------------------------------------------
    // Contact Form Handler
    //-------------------------------------------

    var contactForm = $(".contact-form")
    var contactFormMethod = contactForm.attr("method")
    var contactFormEndpoint = contactForm.attr("action")

    //-------------------------------------------
    // search button spinner
    //-------------------------------------------
    
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

    //----------------------------------------------- 
    // live database search field
    //-----------------------------------------------

    // Get the <datalist> and <input> elements.
    var dataList = document.getElementById('json-datalist');
    var templateList = document.getElementById('template')
    var input = document.getElementById('home-search');
    

    // Create a new XMLHttpRequest.
    var request = new XMLHttpRequest();

    // Handle state changes for the request.
    request.onreadystatechange = function (response) {
            
        if (request.readyState === 4) {
            if (request.status === 200) {
                // ajax call to get products
               
                $.ajax({
                    url: '/search/ajax-search/', // django URL defined
                    dataType: 'json',
                    type: 'post',
                    cache: false,
                    success: function(data){
                        $(data).each(function(index, value){
                            // Create a new <option> element.
                            var option = document.createElement('option');
                            // Set the value using the item in the JSON array.
                            option.text = value.fields.title;
                            
                            // Add the <option> element to the <datalist>.
                            dataList.appendChild(option);
                            templateList.appendChild(option);
                        }
                        )}, 
                        error: function(erroData){
                            console.log("error:", erroData)
                        }

                })    
               

                // Update the placeholder text.
                input.placeholder = "..search..";
            } else {
                // An error occured :(
                input.placeholder = "Couldn't load datalist options :(";
            }
        }
    };

   

    // Update the placeholder text.
    input.placeholder = "Loading options...";

    // Set up and make the request.
    request.open('GET', '/search/ajax-search', true);
    request.send();

    //-------------------------------------------
    // limit the data list to 5 entries shown
    //-------------------------------------------
    
    var search = document.querySelector('#home-search');
    var results = document.querySelector('#json-datalist');
    var templateContent = document.querySelector('#template');
    console.log("template", templateContent)
    console.log(results)
    console.log(search)
    search.addEventListener('keyup', function handler(event) {
        while (results.children.length) results.removeChild(results.firstChild);
        var inputVal = new RegExp(search.value.trim(), 'i');
        var set = Array.prototype.reduce.call(templateContent.cloneNode(true).children, function searchFilter(frag, item, i) {
            if (inputVal.test(item.textContent) && frag.children.length < 6) frag.appendChild(item);
            return frag;
        }, document.createDocumentFragment());
        results.appendChild(set);
    });

    //-------------------------------------------
    // auto search function
    //-------------------------------------------

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

    //-------------------------------------------
    // cart add and remove logic AJAX
    //-------------------------------------------
    var productForm = $(".form-product-ajax")


    //-------------------------------------------
    // digital button
    //-------------------------------------------
    
    function getOwnedProduct(productId, submitSpan){
        var actionEndpoint = '/orders/endpoint/verify/ownership'
        var httpMethod = 'GET'
        var data = {
            product_id: productId,
        }
        var isOwner;
        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: data,
            success: function (data) {
                if (data.owner){
                    isOwner = true
                    submitSpan.html('<a class="btn btn-warning" href="/library/">In Library</a>')
                }else{
                    isOwner = false
                }
            },
            error: function(error){
                console.log(error, "not working")
            }
        })
        
        
        return isOwner
    }

    $.each(productForm, function(index, object){
        var $this = $(this)
        
        var submitSpan = $this.find(".submit-span")
        var productInput = $this.find("[name='product_id']")
        var productId = productInput.attr("value")
        var productIsDigital = productInput.attr("data-is-digital")
        var isUser = productInput.attr("shop-user")
        
        
        if (productIsDigital && isUser){
                var isOwned = getOwnedProduct(productId, submitSpan);
                
        }
    })


    //-------------------------------------------
    // referesh cart function
    //-------------------------------------------
    
    function refreshCart() {
        var cartTable = $(".cart-table");
        var cartBody = cartTable.find(".cart-body");
        var productsRows = cartBody.find(".cart-products")
        var currentUrl = window.location.href

        var cartItemId = productInput.attr("cartitemId")
        var refreshCartUrl = "/api/cart/";
        var refreshCartMethod = "GET";
        var data = {};
        $.ajax({
            url: refreshCartUrl,
            method: refreshCartMethod,
            data: data,
            success: function (data) {
                var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
                if (data.products.length > 0) {
                    productsRows.html(" ")
                    i = data.products.length
                    $.each(data.products, function (index, value) {
                        var newCartItemRemove = hiddenCartItemRemoveForm.clone()
                        newCartItemRemove.css("display", "block")
                        newCartItemRemove.find(".cart-item-product-id").val(data.id)
                        cartBody.prepend("<tr><th scope='row'>" + i + "</th><td>" + value.name + "</td><td>" + value.quantity + "</td><td>" + value.price + "</td><td>" + newCartItemRemove.html() + "</td></tr>")
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