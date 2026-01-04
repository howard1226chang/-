from simulate import load_roles

if __name__ == "__main__":
    roles = load_roles("Roles.json")  
    for role, attrs in roles.items():
        print(f"角色：{role}")
        for key, value in attrs.items():
            print(f"  {key}: {value}")
        print()
    print("✅ Roles.json 欄位驗證通過")
