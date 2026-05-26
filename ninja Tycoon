-- ====================================================================
-- BINH ĐÊM TRẮNG - ANTI BAN & BYPASS PROTECTION
-- ====================================================================

-- 1. Chống lỗi văng game khi treo máy qua đêm (Anti-AFK)
local VirtualUser = game:GetService("VirtualUser")
game:GetService("Players").LocalPlayer.Idled:Connect(function()
    VirtualUser:CaptureController()
    VirtualUser:ClickButton2(Vector2.new(0, 0))
end)

-- 2. Bộ lọc bảo mật: Chặn Game quét Log, Kiểm tra tốc độ (Bypass WalkSpeed/Teleport Detection)
local Namecall
Namecall = hookmetamethod(game, "__namecall", function(Self, ...)
    local Method = getnamecallmethod()
    local Args = {...}
    
    -- Chặn các hàm đá người chơi ra khỏi phòng tự động của hệ thống Anti-Cheat trong game
    if not checkcaller() and (Method == "Kick" or Method == "kick") then
        return nil
    end
    
    -- Chặn game gửi các báo cáo hành vi bất thường (Report/Log) về Server của Admin
    if Method == "FireServer" and Self.Name:lower():find("report") or Self.Name:lower():find("cheat") or Self.Name:lower():find("ban") then
        return nil
    end
    
    return Namecall(Self, ...)
end)

-- 3. Tạo độ trễ ngẫu nhiên siêu nhỏ khi di chuyển để qua mắt hệ thống quét tọa độ tự động (Anti-Detection)
task.spawn(function()
    while task.wait(0.5) do
        local char = game:GetService("Players").LocalPlayer.Character
        local root = char and char:FindFirstChild("HumanoidRootPart")
        if root and _G.batdafarm then
            -- Tạo một độ lệch cực nhỏ (0.01) để vị trí không bị coi là đứng im hoàn hảo/dịch chuyển tức thời tuyệt đối
            root.CFrame = root.CFrame * CFrame.new(math.random(-1, 1)/100, 0, math.random(-1, 1)/100)
        end
    end
end)

print("[Binh Đêm Trắng]: Đã kích hoạt hệ thống Anti-Ban thành công! Đang tải Script...")

-- 4. Gọi file gốc từ GitHub của ông lên chạy dưới sự bảo vệ của lớp Anti-Ban ở trên
loadstring(game:HttpGet("https://raw.githubusercontent.com/nbinh5341-dot/binh-dep-trai/1c154f8343a6a2413d2fe0f2a460f4a04851c25e/ninja%20Tycoon.lua"))()
