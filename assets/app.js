if (!window.dash_clientside) {window.dash_clientside = {};}

window.dash_clientside.clientside = {
    trigger_gsap_animation: function() {
        gsap.registerPlugin(ScrollTrigger);
        gsap.from("#m1", {scrollTrigger: {scrub: true}, x: 200});
        gsap.from("#m2", {scrollTrigger: {scrub: true}, x: 100});
        gsap.from("#t2", {scrollTrigger: {scrub: true}, x: -100});
        gsap.from("#t1", {scrollTrigger: {scrub: true}, x: 50});
        gsap.from("#man", {scrollTrigger: {scrub: true}, x: -200});
        gsap.from("#plants", {scrollTrigger: {scrub: true}, x: -100});
        
        return window.dash_clientside.no_update; // Important for preventing update loops
    },

    scroll_to_map: function(selected_trail) {
        if(selected_trail) {
            setTimeout(function() {
                document.getElementById('trail-map').scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 100); // A slight delay to ensure the DOM has updated
        }
        return window.dash_clientside.no_update; // Prevent updating any Output
    }
}
