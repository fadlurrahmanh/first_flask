async function processCipher(mode){

    const text = document.getElementById("text").value;
    const shift = document.getElementById("shift").value;

    document.getElementById("result").innerHTML = "Processing...";

    const response = await fetch("/caesar/process",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            text:text,
            shift:shift,
            mode:mode
        })

    });

    const data = await response.json();

    document.getElementById("result").innerHTML = data.result;

    let html = "";

    data.steps.forEach(step => {
        html += `<p>${step}</p>`;
    });

    html += `<hr><b>Rumus:</b> ${data.formula}`;

    document.getElementById("steps").innerHTML = html;
}