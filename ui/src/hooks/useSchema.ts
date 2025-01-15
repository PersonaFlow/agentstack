import { useRunnableConfigSchema } from "@/data-provider/query-service"

/*
    {
        scope: "#",
        name: "",
        label: "",
        elements: []
    }
*/

const resolveRef = (ref: string, rootSchema: any) => {
    // console.log(ref)
    if (!ref.startsWith('#')) {
        throw new Error('Ref must start with #')
    }

    const directory = ref.split('/').slice(1)
    
    // console.log(directory)

    let currentLocation = rootSchema
    for (let index of directory) {
        console.log(index)
        // console.log(currentLocation)
        currentLocation = currentLocation[index]
        console.log('currentLocation: ', currentLocation)
        // if (currentLocation === undefined) {
        //     throw new Error('Invalid ref')
        // }
    }
    return currentLocation
}

export const useSchema = () => {

    const { data, isLoading } = useRunnableConfigSchema()
    
    if (!isLoading) {
        resolveRef(data?.properties.configurable.$ref, data)
        // console.log('resolved ref: ',resolveRef(data?.properties.configurable.$ref, data))
    }
    

    return data;
}