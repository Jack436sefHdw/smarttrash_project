async function predictImage(file, container) {
    const label = document.createElement("p");
    label.textContent = "判斷中...";
    container.appendChild(label);
  
    const formData = new FormData();
    formData.append("file", file);
  
    const response = await fetch("http://localhost:5000/predict", {
      method: "POST",
      body: formData,
    });
  
    const data = await response.json();
    label.textContent = `分類結果：${data.result} (信心值: ${(data.confidence * 100).toFixed(1)}%)`;
  
    const correct = document.createElement("button");
    correct.textContent = "正確";
    correct.onclick = () => {
      correct.disabled = true;
      wrong.disabled = true;
      container.remove();  // 僅移除這個 container
    };
  
    const wrong = document.createElement("button");
    wrong.textContent = "錯誤，加入重訓資料";
    wrong.onclick = () => {
      if (container.querySelector("select")) return;  // 防止重複產生
  
      const labelSelect = document.createElement("select");
      labelSelect.innerHTML = `
        <option value="">-- 選擇正確類別 --</option>
        <option value="可回收">可回收</option>
        <option value="不可回收">不可回收</option>
      `;
  
      const submitBtn = document.createElement("button");
      submitBtn.textContent = "確定上傳";
      submitBtn.style.backgroundColor = "#f39c12";
      submitBtn.style.color = "white";
  
      submitBtn.onclick = async () => {
        const selected = labelSelect.value;
        if (!selected) {
          alert("請選擇正確類別");
          return;
        }
        const uploadWrong = new FormData();
        uploadWrong.append("file", file);
        uploadWrong.append("label", selected);
        await fetch("http://localhost:5000/collect_wrong", {
          method: "POST",
          body: uploadWrong,
        });
        alert("✅ 已存下用來重訓");
        correct.disabled = true;
        wrong.disabled = true;
        labelSelect.remove();
        submitBtn.remove();
      };
  
      container.appendChild(labelSelect);
      container.appendChild(submitBtn);
    };
  
    container.appendChild(correct);
    container.appendChild(wrong);
  }
  