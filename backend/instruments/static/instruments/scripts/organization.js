window.addEventListener('load', () => {
  const nameInput = document.getElementById("id_name");
  const acronymInput = document.getElementById("id_acronym");
  const rorIdInput = document.getElementById("id_ror_id");
  rorIdInput.setAttribute("type", "search");
  rorIdInput.setAttribute('dir', "ltr");
  rorIdInput.setAttribute('spellcheck', "false");
  rorIdInput.setAttribute('autocorrect', "off");
  rorIdInput.setAttribute('autocomplete', "off");
  rorIdInput.setAttribute('autocapitalize', "off");
  rorIdInput.parentElement.parentElement.style.overflow = 'visible';
  new autoComplete({
    selector: "#id_ror_id",
    placeHolder: "Search for organization...",
    data: {
      async src(query) {
        try {
          const url = "https://api.ror.org/organizations?" + new URLSearchParams({
            query,
          });
          const res = await fetch(url);
          const data = await res.json();
          return data.items;
        } catch (error) {
          return error;
        }
      },
      keys: ["id"]
    },
    debounce: 300,
    searchEngine(item) {
      return item;
    },
    resultItem: {
      element(item, data) {
        item.innerText = data.value.name;
      }
    },
    events: {
      input: {
        selection(event) {
          const selection = event.detail.selection.value;
          rorIdInput.value = selection.id;
          nameInput.value = selection.name;
          acronymInput.value = selection.acronyms.length > 0 ? selection.acronyms[0] : '';
        }
      }
    }
  });
});
