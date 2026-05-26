-- ====================================================================
-- SCRIPT AUTO FARM: BINH ĐÊM TRẮNG (BẢN FIX TỐI THƯỢNG CHỐNG GHIM PLAYER 100%)
-- ====================================================================
local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")
local CoreGui = game:GetService("CoreGui")
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")

local LocalPlayer = Players.LocalPlayer
local SelectedQueue = {}    
local CurrentQueueIndex = 1 
local SelectedMob = nil     
local SelectedWeaponName = ""
local IsFarming = false
local SavedPosition = nil 

local LOGO_ASSET_ID = "rbxassetid://DÁN_ID_ẢNH_CỦA_ÔNG_VÀO_ĐÂY" 
local CONFIG_FILE = "BinhDemTrang_Config.json"

-- ====================================================================
-- HÀM KIỂM TRA CHÍNH XÁC: CHỈ ĐÁNH QUÁI, KHÔNG ĐÁNH NGƯỜI/CLONE
-- ====================================================================
local function IsRealMob(obj)
    if not obj:IsA("Model") or not obj:FindFirstChild("Humanoid") or not obj:FindFirstChild("HumanoidRootPart") then
        return false
    end
    
    local lowerObjName = string.lower(obj.Name)

    -- 1. Quét danh sách người chơi trong Server để tìm tên clone
    for _, p in pairs(Players:GetPlayers()) do
        local lowerPlayerName = string.lower(p.Name)
        
        -- Kiểm tra nếu tên Model chứa tên người chơi (ví dụ: "Minhnek8586 Clone" chứa "Minhnek8586")
        -- hoặc nếu Model là nhân vật thực của người chơi
        if lowerPlayerName ~= "" and string.find(lowerObjName, lowerPlayerName) then
            return false
        end
        
        if p.Character and obj:IsDescendantOf(p.Character) then
            return false
        end
    end
    
    -- 2. Loại bỏ các NPC thuộc khu vực Tycoon
    if obj:FindFirstAncestor("Tycoon") or string.find(string.lower(obj:GetFullName()), "tycoon") then
        return false
    end

    -- 3. Đảm bảo máu > 0
    if obj.Humanoid.Health <= 0 then
        return false
    end

    return true
end

-- ====================================================================
-- HÀM LƯU VÀ TẢI CẤU HÌNH (AUTO SAVE & LOAD)
-- ====================================================================
local function SaveConfig()
    local config = {
        Queue = SelectedQueue,
        Weapon = SelectedWeaponName
    }
    pcall(function()
        if writefile then
            writefile(CONFIG_FILE, HttpService:JSONEncode(config))
        end
    end)
end

local function LoadConfig()
    pcall(function()
        if readfile and isfile and isfile(CONFIG_FILE) then
            local data = readfile(CONFIG_FILE)
            local config = HttpService:JSONDecode(data)
            if config then
                if config.Queue then SelectedQueue = config.Queue end
                if config.Weapon then SelectedWeaponName = config.Weapon end
                if #SelectedQueue > 0 then IsFarming = true end
            end
        end
    end)
end

LoadConfig()

-- ====================================================================
-- 1. TẠO NÚT TRÒN MÀU TRẮNG THU GỌN (FLOATING BUTTON)
-- ====================================================================
if CoreGui:FindFirstChild("BinhDemTrangGui") then
    CoreGui.BinhDemTrangGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "BinhDemTrangGui"
ScreenGui.Parent = CoreGui

local ToggleButton = Instance.new("TextButton")
ToggleButton.Size = UDim2.new(0, 55, 0, 55)
ToggleButton.Position = UDim2.new(0.1, 0, 0.15, 0)
ToggleButton.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
ToggleButton.Text = "⚔️"
ToggleButton.TextSize = 24
ToggleButton.Active = true
ToggleButton.Draggable = true
ToggleButton.Parent = ScreenGui

local ButtonCorner = Instance.new("UICorner")
ButtonCorner.CornerRadius = UDim.new(1, 0)
ButtonCorner.Parent = ToggleButton

local UIStroke = Instance.new("UIStroke")
UIStroke.Color = Color3.fromRGB(0, 0, 0)
UIStroke.Thickness = 2
UIStroke.Parent = ToggleButton

-- ====================================================================
-- 2. GIAO DIỆN BẢNG ĐIỀU KHIỂN CHÍNH (MAIN FRAME)
-- ====================================================================
local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, 460, 0, 340)
MainFrame.Position = UDim2.new(0.5, -230, 0.5, -170)
MainFrame.BackgroundColor3 = Color3.fromRGB(15, 15, 18)
MainFrame.Visible = false
MainFrame.Active = true
MainFrame.Draggable = true
MainFrame.Parent = ScreenGui

local MainCorner = Instance.new("UICorner")
MainCorner.CornerRadius = UDim.new(0, 12)
MainCorner.Parent = MainFrame

local LogoImage = Instance.new("ImageLabel")
LogoImage.Size = UDim2.new(0, 35, 0, 35)
LogoImage.Position = UDim2.new(0, 15, 0, 10)
LogoImage.BackgroundTransparency = 1
LogoImage.Image = LOGO_ASSET_ID
LogoImage.ScaleType = Enum.ScaleType.Crop
LogoImage.Parent = MainFrame

local LogoCorner = Instance.new("UICorner")
LogoCorner.CornerRadius = UDim.new(1, 0)
LogoCorner.Parent = LogoImage

local ScriptTitle = Instance.new("TextLabel")
ScriptTitle.Size = UDim2.new(0, 200, 0, 35)
ScriptTitle.Position = UDim2.new(0, 60, 0, 10)
ScriptTitle.Text = "BINH ĐÊM TRẮNG ❄️"
ScriptTitle.TextColor3 = Color3.fromRGB(255, 255, 255)
ScriptTitle.Font = Enum.Font.SourceSansBold
ScriptTitle.TextSize = 18
ScriptTitle.TextXAlignment = Enum.TextXAlignment.Left
ScriptTitle.BackgroundTransparency = 1
ScriptTitle.Parent = MainFrame

local RefreshAllBtn = Instance.new("TextButton")
RefreshAllBtn.Size = UDim2.new(0, 40, 0, 30)
RefreshAllBtn.Position = UDim2.new(1, -55, 0, 12)
RefreshAllBtn.BackgroundColor3 = Color3.fromRGB(46, 204, 113)
RefreshAllBtn.Text = "🔄"
RefreshAllBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
RefreshAllBtn.TextSize = 14
RefreshAllBtn.Parent = MainFrame

local RefreshCorner = Instance.new("UICorner")
RefreshCorner.CornerRadius = UDim.new(0, 6)
RefreshCorner.Parent = RefreshAllBtn

local MobSection = Instance.new("Frame")
MobSection.Size = UDim2.new(0, 215, 1, -70)
MobSection.Position = UDim2.new(0, 10, 0, 60)
MobSection.BackgroundTransparency = 1
MobSection.Parent = MainFrame

local MobTitle = Instance.new("TextLabel")
MobTitle.Size = UDim2.new(1, 0, 0, 25)
MobTitle.Text = "🎯 THỨ TỰ DIỆT QUÁI XOAY VÒNG"
MobTitle.TextColor3 = Color3.fromRGB(241, 196, 15)
MobTitle.BackgroundTransparency = 1
MobTitle.Font = Enum.Font.SourceSansBold
MobTitle.TextSize = 12
MobTitle.TextXAlignment = Enum.TextXAlignment.Left
MobTitle.Parent = MobSection

local MobScroll = Instance.new("ScrollingFrame")
MobScroll.Size = UDim2.new(1, 0, 1, -30)
MobScroll.Position = UDim2.new(0, 0, 0, 30)
MobScroll.BackgroundTransparency = 1
MobScroll.ScrollBarThickness = 4
MobScroll.CanvasSize = UDim2.new(0, 0, 0, 0)
MobScroll.Parent = MobSection

local MobListLayout = Instance.new("UIListLayout")
MobListLayout.Parent = MobScroll
MobListLayout.Padding = UDim.new(0, 5)

local WeaponSection = Instance.new("Frame")
WeaponSection.Size = UDim2.new(0, 215, 1, -70)
WeaponSection.Position = UDim2.new(0, 235, 0, 60)
WeaponSection.BackgroundTransparency = 1
WeaponSection.Parent = MainFrame

local WeaponTitle = Instance.new("TextLabel")
WeaponTitle.Size = UDim2.new(1, 0, 0, 25)
WeaponTitle.Text = "⚔️ VŨ KHÍ ĐANG CÓ"
WeaponTitle.TextColor3 = Color3.fromRGB(52, 152, 219)
WeaponTitle.BackgroundTransparency = 1
WeaponTitle.Font = Enum.Font.SourceSansBold
WeaponTitle.TextSize = 13
WeaponTitle.TextXAlignment = Enum.TextXAlignment.Left
WeaponTitle.Parent = WeaponSection

local WeaponScroll = Instance.new("ScrollingFrame")
WeaponScroll.Size = UDim2.new(1, 0, 1, -30)
WeaponScroll.Position = UDim2.new(0, 0, 0, 30)
WeaponScroll.BackgroundTransparency = 1
WeaponScroll.ScrollBarThickness = 4
WeaponScroll.CanvasSize = UDim2.new(0, 0, 0, 0)
WeaponScroll.Parent = WeaponSection

local WeaponListLayout = Instance.new("UIListLayout")
WeaponListLayout.Parent = WeaponScroll
WeaponListLayout.Padding = UDim.new(0, 5)

ToggleButton.MouseButton1Click:Connect(function()
    MainFrame.Visible = not MainFrame.Visible
end)

-- ====================================================================
-- 3. LOGIC DIỆT SẠCH TỪNG CON NGHIÊM NGẶT (BINH ĐÊM TRẮNG)
-- ====================================================================
local function FindNextTargetStrict()
    if #SelectedQueue == 0 then
        SelectedMob = nil
        return
    end

    local attempts = 0
    while attempts < #SelectedQueue do
        local targetName = SelectedQueue[CurrentQueueIndex]
        
        local candidate = nil
        for _, obj in pairs(Workspace:GetDescendants()) do
            if obj.Name == targetName and IsRealMob(obj) then
                candidate = obj
                break 
            end
        end

        if candidate then
            SelectedMob = candidate
            IsFarming = true
            return
        end

        CurrentQueueIndex = CurrentQueueIndex + 1
        if CurrentQueueIndex > #SelectedQueue then
            CurrentQueueIndex = 1 
        end
        attempts = attempts + 1
    end

    SelectedMob = nil
end

-- ====================================================================
-- 4. HÀM TÌM KIẾM TIỀN/RYO RƠI TRÊN MAP (ƯU TIÊN HÀNG ĐẦU)
-- ====================================================================
local function FindValidMoney()
    for _, obj in pairs(Workspace:GetDescendants()) do
        if obj:IsA("BasePart") or obj:IsA("MeshPart") then
            local nameLower = string.lower(obj.Name)
            
            local inTycoon = obj:FindFirstAncestor("Tycoon") or string.find(string.lower(obj:GetFullName()), "tycoon")
            local inShop = obj:FindFirstAncestor("Shop") or string.find(string.lower(obj:GetFullName()), "shop")
            local inSkill = obj:FindFirstAncestor("Skill") or obj:FindFirstAncestorOfClass("BillboardGui")
            
            if not inTycoon and not inShop and not inSkill then
                if string.find(nameLower, "scroll") or string.find(nameLower, "ryo") or string.find(nameLower, "cash") or string.find(nameLower, "money") then
                    return obj 
                end
            end
        end
    end
    return nil
end

-- ====================================================================
-- 5. LUỒNG ĐIỀU KHIỂN TRỰC TIẾP: TIỀN > ĐÁNH CHẾT HẲN QUÁI
-- ====================================================================
RunService.RenderStepped:Connect(function()
    if not IsFarming then return end
    
    local char = LocalPlayer.Character
    local root = char and char:FindFirstChild("HumanoidRootPart")
    if not root then return end

    local targetMoney = FindValidMoney()
    if targetMoney and targetMoney.Parent then
        root.CFrame = targetMoney.CFrame
        root.Velocity = Vector3.new(0, 0, 0)
        return 
    end

    -- Nếu con quái bị khóa không còn thỏa mãn điều kiện là quái thật (ví dụ: máu về 0) thì đổi mục tiêu
    if not SelectedMob or not IsRealMob(SelectedMob) then
        if SelectedMob then 
            CurrentQueueIndex = CurrentQueueIndex + 1
            if CurrentQueueIndex > #SelectedQueue then
                CurrentQueueIndex = 1
            end
        end
        
        FindNextTargetStrict()
        return
    end

    local mobRoot = SelectedMob.HumanoidRootPart
    SavedPosition = mobRoot.CFrame

    root.CFrame = mobRoot.CFrame * CFrame.new(0, 1, 0)
    root.Velocity = Vector3.new(0, 0, 0)

    mobRoot.CFrame = root.CFrame * CFrame.new(0, -1, 0)
    mobRoot.Velocity = Vector3.new(0, 0, 0)
end)

task.spawn(function()
    while true do
        task.wait(0.1)
        if IsFarming and SelectedMob and SelectedWeaponName ~= "" then
            if not FindValidMoney() then
                local char = LocalPlayer.Character
                local backpack = LocalPlayer:FindFirstChild("Backpack")
                
                if char then
                    local currentTool = char:FindFirstChild(SelectedWeaponName)
                    if not currentTool and backpack then
                        local targetTool = backpack:FindFirstChild(SelectedWeaponName)
                        if targetTool then
                            targetTool.Parent = char
                            currentTool = targetTool
                        end
                    end
                    if currentTool and currentTool:IsA("Tool") then
                        currentTool:Activate()
                    end
                end
            end
        end
    end
end)

-- ====================================================================
-- 6. HÀM CẬP NHẬT GIAO DIỆN VÀ QUẢN LÝ HÀNG ĐỢI TUẦN TỰ
-- ====================================================================
local function RefreshData()
    for _, child in pairs(MobScroll:GetChildren()) do if child:IsA("TextButton") then child:Destroy() end end
    for _, child in pairs(WeaponScroll:GetChildren()) do if child:IsA("TextButton") then child:Destroy() end end

    local mobCount = 0
    local addedMobNames = {} 

    local function getQueueIndex(name)
        for idx, v in ipairs(SelectedQueue) do
            if v == name then return idx end
        end
        return nil
    end

    for _, obj in pairs(Workspace:GetDescendants()) do
        -- Chỉ hiện tên những con được xác nhận là quái thật lên menu
        if IsRealMob(obj) and not addedMobNames[obj.Name] then
            addedMobNames[obj.Name] = true
            mobCount = mobCount + 1

            local MobBtn = Instance.new("TextButton")
            MobBtn.Size = UDim2.new(1, -5, 0, 32)
            
            local qIdx = getQueueIndex(obj.Name)
            if qIdx then
                MobBtn.BackgroundColor3 = Color3.fromRGB(231, 76, 60)
                MobBtn.Text = string.format("[%d] 🔥 ĐANG CHỌN: %s", qIdx, obj.Name)
            else
                MobBtn.BackgroundColor3 = Color3.fromRGB(44, 62, 80)
                MobBtn.Text = "🎯 Tích chọn: " .. obj.Name
            end
            
            MobBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
            MobBtn.Font = Enum.Font.SourceSansBold
            MobBtn.TextSize = 11
            MobBtn.Parent = MobScroll

            local Corner = Instance.new("UICorner")
            Corner.CornerRadius = UDim.new(0, 4)
            Corner.Parent = MobBtn

            MobBtn.MouseButton1Click:Connect(function()
                local currentIdx = getQueueIndex(obj.Name)
                if currentIdx then
                    table.remove(SelectedQueue, currentIdx)
                else
                    table.insert(SelectedQueue, obj.Name)
                end
                
                SaveConfig()
                
                CurrentQueueIndex = 1
                SelectedMob = nil 
                IsFarming = (#SelectedQueue > 0)
                RefreshData()
                FindNextTargetStrict()
            end)
        end
    end
    MobScroll.CanvasSize = UDim2.new(0, 0, 0, mobCount * 37)

    local weaponCount = 0
    local foundWeapons = {}
    local function checkAndAddWeapon(tool)
        if tool:IsA("Tool") and not foundWeapons[tool.Name] then
            foundWeapons[tool.Name] = true
            weaponCount = weaponCount + 1
            local WeapBtn = Instance.new("TextButton")
            WeapBtn.Size = UDim2.new(1, -5, 0, 32)
            if SelectedWeaponName == tool.Name then
                WeapBtn.BackgroundColor3 = Color3.fromRGB(155, 89, 182)
                WeapBtn.Text = "🔒 KHÓA: " .. tool.Name
            else
                WeapBtn.BackgroundColor3 = Color3.fromRGB(52, 73, 94)
                WeapBtn.Text = "⚔️ Dùng: " .. tool.Name
            end
            WeapBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
            WeapBtn.Font = Enum.Font.SourceSansBold
            WeapBtn.TextSize = 12
            WeapBtn.Parent = WeaponScroll
            local Corner = Instance.new("UICorner")
            Corner.CornerRadius = UDim.new(0, 4)
            Corner.Parent = WeapBtn
            WeapBtn.MouseButton1Click:Connect(function()
                SelectedWeaponName = tool.Name
                SaveConfig()
                
                for _, btn in pairs(WeaponScroll:GetChildren()) do
                    if btn:IsA("TextButton") then
                        btn.BackgroundColor3 = Color3.fromRGB(52, 73, 94)
                        btn.Text = "⚔️ Dùng: " .. btn.Text:gsub("🔒 KHÓA: ", ""):gsub("⚔️ Dùng: ", "")
                    end
                end
                WeapBtn.BackgroundColor3 = Color3.fromRGB(155, 89, 182)
                WeapBtn.Text = "🔒 KHÓA: " .. tool.Name
            end)
        end
    end
    local backpack = LocalPlayer:FindFirstChild("Backpack")
    if backpack then for _, t in pairs(backpack:GetChildren()) do checkAndAddWeapon(t) end end
    local char = LocalPlayer.Character
    if char then for _, t in pairs(char:GetChildren()) do checkAndAddWeapon(t) end end
    WeaponScroll.CanvasSize = UDim2.new(0, 0, 0, weaponCount * 37)
end

RefreshAllBtn.MouseButton1Click:Connect(RefreshData)
RefreshData()

if #SelectedQueue > 0 then
    FindNextTargetStrict()
end
