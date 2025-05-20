<script lang="ts">
  import { onMount } from "svelte";
  import TodayBalanceModal from "../modals/TodayBalanceModal.svelte"; // 引入 TodayBalanceModal

  let showModal = $state(false); // 用 $state 来声明 showModal 为响应式变量
  let balance = $state("Loading..."); // 用 $state 来声明 balance 为响应式变量
  const { onClose } = $props(); // 获取传递的 onClose
  // 获取今日余额的 API 请求
  onMount(async () => {
    try {
      const res = await fetch("/api/today_balance");
      const data = await res.json();
      balance = `${data.balance} USD`; // 更新余额
    } catch (e) {
      balance = "Error fetching data"; // 请求失败时显示错误信息
    }
  });
</script>

<!-- 显示今日余额按钮 -->
<li>
  <button
    onclick={() => (showModal = true)}
    style="width:100%;padding:0.25em 0.5em 0.25em 1em;font:inherit;color:inherit;text-align:left;cursor:pointer;background:none;border:none;"
  >
    📊 今日余额
  </button>
</li>

<!-- 显示模态框 -->
{#if showModal}
  <TodayBalanceModal {onClose} {balance} />
{/if}
